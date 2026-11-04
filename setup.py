from setuptools import setup, find_packages

setup(
    name="texera-rudf",
    version="0.2.0",
    description="R language support plugin for Apache Texera",
    packages=find_packages(),
    package_data={"texera_r": ["ui_parameters.R"]},
    python_requires=">=3.10,<3.13",
    license="MIT",
    install_requires=[
        "rpy2==3.5.11",
        "rpy2-arrow==0.0.8",
    ],
)
