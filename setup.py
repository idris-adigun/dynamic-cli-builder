from setuptools import setup, find_packages

setup(
    name="dynamic-cli-builder",
    version="0.1.0",
    description="A Python library for dynamically building CLI tools from YAML configurations.",
    author="Idris Adigun",
    author_email="adigun.idris@ymail.com",
    url="https://github.com/idris-adigun/dynamic-cli-builder",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "dynamic-cli=dynamic_cli_builder.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
