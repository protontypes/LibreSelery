<img align="middle" src="./docs/design/OpenSelery-04.svg" width="512">     

> Software-Defined Funding Distribution

[![Actions Status](https://github.com/protontypes/openselery/workflows/openselery/badge.svg)](https://github.com/protontypes/openselery/actions)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/openselery/openselery)

__[Project Slides](http://protontypes.eu:1313/)__
> Please keep in mind that OpenSelery is in an experimental state. The amount of funding should therefore be kept to a minimum.

## Contribution
Constributors on the master branch will probably get emails with cryptocurrency. Only git profiles with emails on the github profile page are considered. We will never send a URL in the note.

## Usage
1. Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

```bash
cd ~
git clone https://github.com/openselery/openselery.git
cd openselery
./build.sh
```

2. Create a dedicated coinbase account with limited amounts. 
3. Never transfer or store large values with automated cryptocurrency wallets. Use recurring automated transaction from another account to recharge you wallet on a regular base. 
4. Transfer some money to this wallet for testing.  
5. Add your tokens from the coinbase API:      

```bash
nano ~/.openselery/tokens.env

COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# NEVER PRINT THIS

# You will need the COINBASE TOKEN and SECRECT when setting simulation=False.
```

6. Configure your distribution in your CI Script or a seler.yml on top of your project. simulation is set True by default. 


7. Run OpenSelery on the project folder you want to fund. This will send cryptocurrency to weighted random product contributors with a valid email address on the git platform or git commit:    

```bash
env $(cat ~/.openselery/tokens.env) ~/openselery/run.sh <target_directory>
```
8. You can integrate OpenSelery in your CI with the template yml file.
```
cat .github/actions/openselery.yml 
```

*Artwork by Miriam Winter*
