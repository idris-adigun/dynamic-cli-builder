from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dynamic_cli_builder",
    version="0.2.1",
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
            "dcb=dynamic_cli_builder.__main__:main",
            "dynamic-cli-builder=dynamic_cli_builder.__main__:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
