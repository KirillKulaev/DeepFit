# DeepFit: Physically and Chemically Informed XAS-Structure Fitting

DeepFit is a deep learning approach for physically and chemically informed on-the-fly XANES spectra analysis. This package provides a unified framework for quantitative XANES analysis that combines spectroscopic sensitivity with quantum-chemical energy constraints.

## Installation

```bash
pip install deepfit_package
```


## Usage Examples

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
experimental_spectrum = load_your_spectrum()

struct = Structure(xyz, absorber='Rh', charge=0, device='cpu') # Nota Bene: spin states for unpaired electron number, not the spin multiplicity number!
deepfit = DeepFit(struct,
                  spectrum,
                  model=Net(device='cpu'),
                  path2xtb=path2xtb, # path for xtb.exe file for forces estimation
                  step_speed=0.125,
                  forces_coeff=2., # Balance between spectral fit and energy minimization
                  fit_edges=(1.5, 8)) # Boundaries of k, on which the spectrum differences are calculated

refined_structure, refined_spectra = deepfit.run(verbose=1,
                                                 num_steps=200,
                                                 final_geomopt=True, 
                                                 distance_weightning=True)
```

### Spectrum Prediction

```python
# Predict spectrum for a given structure
xyz = """Rh 0.0 0.0 0.0
O  1.8  0.0  0.0
O  0.0  1.8  0.0
O  0.0  0.0  1.8
O -0.9 -0.9 -0.9
"""
struct = Structure(xyz, absorber='Rh', charge=0, device='cpu') # Nota Bene: spin states for unpaired electron number, not the spin multiplicity number!
predicted_spectrum = model(structure_data)
```

## Method Overview

DeepFit is a method for structure-XAS fitting. The optimization objective combines spectral agreement and chemical plausibility:

```
$R* = \argmin[R] [D(X,\mathbf{R},\chi(k)) + \lambda E(\mathbf{R})]$
```

Where:
- $D(X,\mathbf{R},\chi(k))$ is the spectral deviation between predicted and experimental spectra
- $E(\mathbf{R})$ is the quantum-mechanical energy of the system
- $\lambda$ is a parameter balancing spectroscopic and energetic constraints

## Supported Elements

DeepFit supports K-edge analysis for:
- **3d metals**: Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn
- **4d metals**: Zr, Nb, Mo, Ru, Rh, Pd, Ag

## Citation

If you use DeepFit in your research, please cite:

```bibtex
@article{deepfit2025,
  title={DeepFit: physically and chemically informed XAS-Structure fitting made simple},
  author={Kulaev Kirill, Protsenko Bogdan, Alexander Guda, Sergey Guda, Mikhail Soldatov, Alexander Soldatov and others},
  journal={To be published},
  year={2025}
}
```
## Support

For questions and support, please open an issue on GitHub or contact the development team.

## Acknowledgments

This work was supported by the Russian Science Foundation (Project No. 24-43-00215) and the Strategic Academic Leadership Program of the Southern Federal University ("Priority 2030").
