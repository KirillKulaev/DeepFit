import os
import subprocess
import torch
import numpy as np
from tqdm import tqdm
from torch_geometric.data import Data

descriptors = np.load(f'descriptors.npz')

periodic_table = {'h': 1, 'he': 2, 'li': 3, 'be': 4, 'b': 5, 'c': 6, 'n': 7, 'o': 8, 'f': 9, 'ne': 10, 
                  'na': 11, 'mg': 12, 'al': 13, 'si': 14, 'p': 15, 's': 16, 'cl': 17, 'ar': 18, 
                  'k': 19, 'ca': 20, 'sc': 21, 'ti': 22, 'v': 23, 'cr': 24, 'mn': 25, 'fe': 26, 
                  'co': 27, 'ni': 28, 'cu': 29, 'zn': 30, 'ga': 31, 'ge': 32, 'as': 33, 'se': 34, 
                  'br': 35, 'kr': 36, 'rb': 37, 'sr': 38, 'y': 39, 'zr': 40, 'nb': 41, 'mo': 42, 
                  'tc': 43, 'ru': 44, 'rh': 45, 'pd': 46, 'i': 53}

def integral(x,y):
    if len(y.shape) == 1:
        my = (y[1:]+y[:-1])/2
    else:
        my = (y[:, 1:] + y[:,:-1]) / 2
    dx = x[1:] - x[:-1]
    return torch.dot(my, dx)

def get_normed_spectra(spectra, k):
    l1_norm = integral(k, torch.abs(spectra))
    normed_spectra = 1./l1_norm * spectra
    return normed_spectra


def masked_normed_l1(candidate_signal, ref_spectra, k, left, right):
    mask = (k > left) & (right < 8.)
    candidate_signal = candidate_signal[mask]
    ref_spectra = ref_spectra[0][mask]
    k = k[mask]
    normed_candidate_signal = get_normed_spectra(candidate_signal, k)
    normed_ref_spectra = get_normed_spectra(ref_spectra, k)
    deviation = integral(k, (normed_candidate_signal - normed_ref_spectra)**2)
    return deviation


class Structure():
    def __init__(self, xyz, charge=0, spin=0, absorber='Rh', device='cuda'):
        xyz = xyz
        self.absorber = absorber
        self.charge = charge
        self.spin = spin
        self.device = device
        self.elements = [i.split()[0] for i in xyz.splitlines()]
        self.pos = torch.tensor([[float(i.split()[1]), float(i.split()[2]), float(i.split()[3])] for i in xyz.splitlines()], dtype=torch.float32, device=device)
        self.pos.requires_grad = True
        features = descriptors
        features = np.array([features[str(periodic_table[i.lower()])] for i in self.elements])
        abs_idx = np.array([1. if i == absorber else 0. for i in self.elements]).reshape(-1, 1)
        self.x = torch.tensor(np.hstack([abs_idx, features]), dtype=torch.float32, device=device)
        self.data = Data(x=self.x, pos=self.pos)


class DeepFit():
        def __init__(self, structure, spectra, model, tmp_folder='tmp_folder', path2xtb='xtb', step_speed=0.01, forces_coeff=1., fit_edges=(-3, 8.5)):
            os.system(f'mkdir {tmp_folder}')
            self.tmp_folder = tmp_folder
            self.structure = structure
            self.spectra = torch.tensor(spectra, dtype=torch.float32, device=structure.device)
            self.model = model
            self.history = []
            self.history_spec = []
            self.optimizer = torch.optim.Adam([self.structure.data['pos']], lr=step_speed)
            self.forces_coeff = forces_coeff
            self.criteria = self.normed_l2
            self.mask = (model.k > fit_edges[0]) & (model.k < fit_edges[1])
            self.xtb_grad_call = f"cd {tmp_folder} && {path2xtb} process_structure.xyz --chrg {structure.charge} --uhf {structure.spin} --grad"
            self.history_sp_loss = []
            self.history_energy = []

    
        @staticmethod
        def normed_l2(candidate_signal, ref_spectra, k, mask):    
            candidate_signal = candidate_signal[mask]
            ref_spectra = ref_spectra[mask]
            k = k[mask] 
            normed_candidate_signal = get_normed_spectra(candidate_signal, k)
            normed_ref_spectra = get_normed_spectra(ref_spectra, k)
            deviation = integral(k, (normed_candidate_signal - normed_ref_spectra)**2)
            return deviation
        
        def objectiveFunction(self, candidate_data):
            candidate_signal = self.model(candidate_data.data)[0]
            self.candidate_signal = candidate_signal
            deviation = self.criteria(self.spectra, candidate_signal, self.model.k, self.mask)
            return deviation
    
        def get_xtb_forces(self, xyz):
            with open(f'{self.tmp_folder}/process_structure.xyz', 'w') as f:
                f.write(str(len(xyz.splitlines()))+'\n\n'+xyz)
            s = subprocess.run(self.xtb_grad_call, shell=True, text=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            forces = self.parse_grad()
            return forces

    
        def parse_grad(self):
            with open(f'{self.tmp_folder}/gradient', 'r') as f:
                lines = f.read().splitlines()
                forces = [[float(g.split()[0]), float(g.split()[1]), float(g.split()[2])] for g in lines[len(lines)//2+1:-1]]
            return torch.tensor(forces).to(self.structure.device)

        def parse_energy(self):
            with open(f'{self.tmp_folder}/energy', 'r') as f:
                energy = float(f.read().splitlines()[1].split()[1])
            return torch.tensor(energy).to(self.structure.device)

    
        @staticmethod
        def struct2xyz(struct):
            return '\n'.join([f'{i} {float(j[0])} {float(j[1])} {float(j[2])}' for i, j in zip(struct.elements, struct.pos)])

    
        def run(self, num_steps=500, verbose=1, final_geomopt=False, distance_weightning=False):
            print(f'Fitting of the structure')
            for iteration in tqdm(range(num_steps)):
                
                def closure():
                    self.optimizer.zero_grad()
                    loss = self.objectiveFunction(self.structure)
                    loss.backward()
                    xyz = self.struct2xyz(self.structure)
                    forces = self.get_xtb_forces(xyz)
                    energy = self.parse_energy()

                    if distance_weightning:
                        i = (np.array(self.structure.elements) == self.structure.absorber).argmax()
                        dist_to_absorber = torch.sqrt(((self.structure.data['pos'] - self.structure.data['pos'][i])**2).sum(axis=1)).view(-1, 1)
                        self.structure.data['pos'].grad = self.weight_distance(dist_to_absorber)*self.structure.data['pos'].grad + self.forces_coeff*forces
                    else:
                        self.structure.data['pos'].grad += self.forces_coeff*forces

                    if final_geomopt and (num_steps - iteration) < 10:
                        self.structure.data['pos'].grad = self.forces_coeff*forces
                        
                    if verbose == 1 and iteration % 5 == 0:
                        print(f'Spectra deviation L2 norm: {float(loss)}, Energy: {float(energy)}, Forces norm: {torch.abs(forces).mean()}')
                        
                    self.history.append(xyz)
                    self.history_spec.append(self.candidate_signal.detach().cpu().numpy())
                    self.history_sp_loss.append(float(loss))
                    self.history_energy.append(float(energy))
                    return loss
                    
                self.optimizer.step(closure)
            final_spectra = self.model(self.structure.data).detach().cpu().numpy()
            return self.structure, final_spectra

        @staticmethod
        def weight_distance(r, u=0.4):
            return torch.exp(- u**2 * r**2)
    
        def eval_stability(self, xyz, absorber, radii=3.5):
            mask = []
            for a in xyz.splitlines():
                if a.split()[0] == absorber:
                    center_coords = np.array([float(i) for i in a.split()[1:]])
            for a in xyz.splitlines():
                coord = np.array([float(i) for i in a.split()[1:]])
                r = np.sqrt(((coord - center_coords)**2).sum())
                if r < radii:
                    mask.append(True)
                else:
                    mask.append(False)
            forces = self.get_xtb_forces(xyz).cpu().numpy()
            local_forces = forces[mask]
            norm_grad = np.mean(np.abs(local_forces))
            return norm_grad

