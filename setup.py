from setuptools import setup , find_packages 
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="MLOPS THIRD PROJECT",
    version="0.1",
    author="Michel",
    packages=find_packages(),
    install_requires=requirements,
)
# pip install -e . -> this will find setup.py and install all the required