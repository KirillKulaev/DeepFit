from setuptools import setup

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    REQUIRED_PACKAGES = f.read().splitlines()

# Define package data
PACKAGE_DATA = [
    "model/*.npz",
    "model/weights/*",
]

setup(
    name="deepfit_package",
    version="0.1.0",
    description="DeepFit: physically and chemically informed XAS-Structure fitting made simple",
    url="https://github.com/KirillKulaev/DeepFit",
    author="Kirill Kulaev, Bogdan Procenko",
    author_email="<your-email@example.com>",
    # Explicitly define packages instead of using find_packages
    packages=["deepfit_package", "deepfit_package.model"],
    package_data={
        "deepfit_package": PACKAGE_DATA,
    },
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