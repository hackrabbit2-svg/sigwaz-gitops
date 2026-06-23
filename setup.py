from setuptools import setup, find_packages

setup(
    name="sigwaz-gitops",
    version="1.0.0",
    description="A backend GitOps plugin to sync Sigma rules to Wazuh.",
    author="Detection Engineering Team",
    packages=find_packages(),
    install_requires=[
        "GitPython>=3.1.0",
        "ruamel.yaml>=0.17.0",
    ],
    entry_points={
        "console_scripts": [
            "sigwaz-sync=sigwaz_sync.cli:main", 
        ],
    },
)