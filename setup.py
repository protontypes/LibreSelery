#! /usr/bin/env python3
from setuptools import setup
from glob import glob

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
        "dnspython",
        "pyyaml",
        "coinbase",
        "gitpython",
        "pybraries",
        "urlextract",
        "matplotlib",
        "numpy",
        "prompt_toolkit",
        "qrcode",
        "wheel",
        "pluginlib",
        "python-dotenv",
        "markdown",
        "bs4",
    ],
    packages=[
        "libreselery",
    ],
    scripts=[
        "scripts/selery",
    ],
    ### add additional files to $TARGET_DIR containing [$SOURCE_FILES]
    data_files=[
        ("libreselery/contribution_activity_plugins", glob("libreselery/contribution_activity_plugins/*.py"))
    ],
)
