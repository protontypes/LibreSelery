from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Protontypes',
    packages=['protontypes',],
    long_description=open('README.md').read(),
    install_requires=requirements
)

