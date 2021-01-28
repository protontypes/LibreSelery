#! /usr/bin/env python3
from setuptools import setup

### https://setuptools.readthedocs.io/en/latest/setuptools.html

import os

pwd = os.path.abspath(os.path.dirname(__file__))
### Get the long description from the README file
with open(os.path.join(pwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

### package definition
setup(
    name="libreselery",
    version_format="{tag}.dev{commitcount}",
    setup_requires=["setuptools-git-version"],
    description="A Software-Defined Funding Distribution",
    url="https://github.com/protontypes/libreselery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    dependency_links=[
        "https://github.com/protontypes/coinbase-python/tarball/master#egg=coinbase"
    ],
    install_requires=[
        "pygithub==1.52",
        "dnspython==2.0.0",
        "pyyaml==5.3.1",
        "coinbase",
        "idna==2.7",
        "gitpython==3.1.7",
        "pybraries==0.3.0",
        "urlextract==1.0.0",
        "matplotlib==3.3.0",
        "numpy==1.19.1",
        "prompt_toolkit",
        "qrcode",
        "wheel",
    ],
    packages=[
        "libreselery",
    ],
    scripts=[
        "scripts/selery",
    ],
    ### add additional files to $TARGET_DIR containing [$SOURCE_FILES]
    data_files=[
        ("libreselery/ruby_extensions", ["libreselery/ruby_extensions/scan.rb"]),
    ],
    package_dir={"libreselery": "libreselery"},
    package_data={"libreselery": ["../selery.yml"]},
)
