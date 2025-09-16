from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    REQUIRED_PACKAGES = f.read().splitlines()

# Get package directory
package_dir = "deepfit_package"

setup(
    name="deepfit_package",
    version="0.1.0",
    description="DeepFit: physically and chemically informed XAS-Structure fitting made simple",
    url="https://github.com/KirillKulaev/DeepFit",
    author="Kirill Kulaev, Bogdan Procenko",
    author_email="<your-email@example.com>",
    packages=find_packages(),
    package_dir={"deepfit_package": "deepfit_package"},
    package_data={
        "deepfit_package": [
            "model/*.npz",
            "model/weights/*",
        ]
    },
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES,
    python_requires=">=3.7",
    license="Apache 2.0",
    entry_points={
        "console_scripts": [
            "deepfit=deepfit_package.deepfit:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)