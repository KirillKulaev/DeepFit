# DeepFit: Physically and Chemically Informed XAS-Structure Fitting

DeepFit is a deep learning approach for physically and chemically informed on-the-fly XANES spectra analysis. This package provides a unified framework for quantitative XANES analysis that combines spectroscopic sensitivity with quantum-chemical energy constraints.

## Installation

```bash
pip install deepfit_package
```

## Quick Start

```python
import deepfit_package
from deepfit_package import DeepFit, Structure

# Create a structure from XYZ coordinates
xyz = """Rh 0.0 0.0 0.0
O 1.8 0.0 0.0
N 0.0 1.8 0.0
C 0.0 0.0 1.8"""

structure = Structure(xyz, absorber='Rh', charge=0, spin=0)

# Load your experimental spectrum (numpy array)
experimental_spectrum = load_your_spectrum()

# Initialize DeepFit with your model
deepfit = DeepFit(structure, experimental_spectrum, model_path='path/to/model')

# Run structure refinement
refined_structure, final_spectrum = deepfit.run(num_steps=200)
```

## Usage Examples

### Structure Refinement

```python
# Basic structure refinement
refined_structure, predicted_spectrum = deepfit.run(num_steps=200, verbose=1)

# With energy constraints ($\lambda$ parameter)
refined_structure, predicted_spectrum = deepfit.run(
    num_steps=200, 
    lambda=2.0,  # Balance between spectral fit and energy minimization
    verbose=1
)
```

### Spectrum Prediction

```python
# Predict spectrum for a given structure
predicted_spectrum = model.predict(structure_data)

# Compare with experimental data
deviation = deepfit.normed_l2(predicted_spectrum, experimental_spectrum, k_values, mask)
```

## Method Overview

DeepFit is a method for structure-XAS fitting. The optimization objective combines spectral agreement and chemical plausibility:

```
R* = argmin[R] [D(X,R,χ) + λE(R)]
```

Where:
- $D(X,R,\chi(k))$ is the spectral deviation between predicted and experimental spectra
- $E(R)$ is the quantum-mechanical energy of the system
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
  author={Kulaev, Kirill and Protsenko, Bogdan and Cheng, Weiren and others},
  journal={To be published},
  year={2025}
}
```
## Support

For questions and support, please open an issue on GitHub or contact the development team.

## Acknowledgments

This work was supported by the Russian Science Foundation (Project No. 24-43-00215) and the Strategic Academic Leadership Program of the Southern Federal University ("Priority 2030").
