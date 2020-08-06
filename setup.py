#! /usr/bin/env python3
from setuptools import setup
### https://setuptools.readthedocs.io/en/latest/setuptools.html

import os

### read requirements file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
    
pwd = os.path.abspath(os.path.dirname(__file__))
### Get the long description from the README file
with open(os.path.join(pwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
### package definition
setup(
    name='openselery',
    #version='0.1',
    ### use 
    ### https://github.com/pyfidelity/setuptools-git-version
    ### instead of normal version :)
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version'],

    description='A Software-Defined Funding Distribution',
    url='https://github.com/kikass13/openselery',
    long_description=long_description,
    install_requires=requirements,

    packages=['openselery',],
    scripts=['scripts/selery',],

    ### add additional files to $TARGET_DIR containing [$SOURCE_FILES]
    data_files=[("openselery/ruby_extensions", ["openselery/ruby_extensions/scan.rb"])],

)
