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
    name="openselery",
    version_format="{tag}.dev{commitcount}",
    setup_requires=["setuptools-git-version"],
    description="A Software-Defined Funding Distribution",
    url="https://github.com/protontypes/openselery",
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
        "gitpython==3.1.7",
        "pybraries==0.2.2",
        "urlextract==1.0.0",
        "matplotlib==3.3.0",
        "numpy==1.19.1",
        "qrcode",
        "wheel",
    ],
    packages=["openselery",],
    scripts=["scripts/selery",],
    ### add additional files to $TARGET_DIR containing [$SOURCE_FILES]
    data_files=[("openselery/ruby_extensions", ["openselery/ruby_extensions/scan.rb"])],
)
