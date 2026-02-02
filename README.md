# DeepFit: Physically and Chemically Informed XAS-Structure Fitting Made Simple

DeepFit is a deep learning approach for physically and chemically informed on-the-fly XANES spectra analysis. This package provides a unified framework for quantitative XANES analysis that combines spectroscopic sensitivity with quantum-chemical energy constraints.

## Installation

```bash
git clone https://github.com/KirillKulaev/DeepFit.git
pip install ./DeepFit
```


## Usage Examples

### Spectrum Prediction

```python
# Predict spectrum for a given structure
from deepfit_package import Net, Structure
model = Net()

xyz = """Rh 0.0 0.0 0.0
O  1.8  0.0  0.0
O  0.0  1.8  0.0
O  0.0  0.0  1.8
O -0.9 -0.9 -0.9
"""

struct = Structure(xyz, absorber='Rh', charge=0, device='cpu')
predicted_spectrum = model(struct.data)
```

### Structure Refinement

```python
# Structure refinement
import deepfit_package
from deepfit_package import DeepFit, Structure, Net

# Create a structure from XYZ coordinates
xyz = """Rh 0.0 0.0 0.0
O  1.8  0.0  0.0
O  0.0  1.8  0.0
O  0.0  0.0  1.8
O -0.9 -0.9 -0.9
"""

# Load your experimental spectrum (numpy array)
experimental_spectrum = load_your_spectrum() # change for your actual spectrum loading

struct = Structure(xyz, absorber='Rh', charge=0, device='cpu') # Nota Bene: spin states for unpaired electron number, not the spin multiplicity number!
deepfit = DeepFit(struct,
                  spectrum,
                  model=Net(device='cpu'),
                  path2xtb='../xtb', # path for xtb.exe file for forces estimation
                  step_speed=0.125,
                  forces_coeff=2., # Balance between spectral fit and energy minimization
                  fit_edges=(1.5, 8)) # Boundaries of k, on which the spectrum differences are calculated

refined_structure, refined_spectra = deepfit.run(verbose=1,
                                                 num_steps=200,
                                                 final_geomopt_steps=0, 
                                                 distance_weightning=True)
```


## Method Overview

DeepFit is a method for structure-XAS fitting. The optimization objective combines spectral agreement and chemical plausibility:

```math
R^* = \arg\min_{R} \left[ D[X,\mathbf{R},\chi(k)] + \lambda E(\mathbf{R}) \right]
```

Where:
- $D(X,\mathbf{R},\chi(k))$ is the spectral deviation between predicted and experimental spectra
- $E(\mathbf{R})$ is energy of the system
- $\lambda$ is a parameter balancing spectroscopic and energetic constraints

## Supported Elements

DeepFit supports K-edge analysis for:
- **3d metals**: Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn
- **4d metals**: Zr, Nb, Mo, Ru, Rh, Pd, Ag
- in any organic coordination environment

## Citation

If you use DeepFit in your research, please cite:

```bibtex
@article{deepfit2025,
  title={DeepFit: physically and chemically informed XAS-Structure fitting made simple},
  author={Kulaev Kirill, Protsenko Bogdan, Alexander Guda, Sergey Guda, Mikhail Soldatov, Alexander Soldatov and others},
  url={http://dx.doi.org/10.26434/chemrxiv-2025-xn5zb-v2},
  journal={To be published},
  year={2025}
}
```
## Support

For questions and support, please open an issue on GitHub or contact the development team.

## Acknowledgments

The development of DeepFit framework was supported by a grant from the Russian Science Foundation № 25-42-00116, https://rscf.ru/project/25-42-00116/, National Natural Science Foundation of China (China-Russia Cooperation Program, No.: W2412038) and the International Partnership Program of Chinese Academy of Sciences (Grant No.123GJHZ2024102FN). Rh K-edge XAS experiment and data analysis was supported by the strategic Academic Leadership Program of the Southern Federal University (“Priority 2030”). Authors acknowledge methodological support and computational resources from Yandex Cloud Center for Social Technologies (https://yandex.cloud/en/social-tech) for training neural networks.
