from setuptools import setup, find_packages
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def increment_version(version):
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"

with open("setup.py", "r", encoding="utf-8") as fh:
    setup_content = fh.read()

new_version = increment_version("0.1.15")
setup_content = re.sub(r'version="[\d\.]+",', f'version="{new_version}",', setup_content)

with open("setup.py", "w", encoding="utf-8") as fh:
    fh.write(setup_content)

setup(
    name="dynamic_cli_builder",
    version=new_version,
    description="A Python library for dynamically building CLI tools from YAML configurations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Idris Adigun",
    author_email="adigun.idris@ymail.com",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "dynamic-cli=dynamic_cli_builder:run_builder",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
