from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
    
here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name='openselery',
    packages=['openselery',],
    long_description=long_description,
    install_requires=requirements
)

