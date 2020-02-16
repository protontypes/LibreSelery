<img align="middle" src="./docs/design/OpenSelery-04.svg" width="400"> 

> Automated Open Source Funding 

[![Actions Status](https://github.com/protontypes/openselery/workflows/openselery/badge.svg)](https://github.com/protontypes/openselery/actions)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/openselery/openselery)

* [Project Slides](http://protontypes.eu:1313/)
* [Roadmap](https://github.com/protontypes/openselery/wiki)
* [Knowledge-Links](https://github.com/protontypes/openselery/wiki/Knowledge-Links)

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

2. Create a dedicated coinbase account with limited amounts. OpenSelery is based on the APIs of The Libraries.io, Github and Coinbase. To provide service you need create to tokens in the corresponding accounts. Setting simulation to false will require your coinbase tokens.
3. Never transfer or store large values with automated cryptocurrency wallets. Use recurring automated transaction from another account to recharge you wallet on a regular base. 
4. Transfer some money to this wallet for testing. See the [price list](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/fees.html) for transfering money to the coinbase account.
5. Add your tokens API: 

```bash
nano ~/.openselery/tokens.env

COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# NEVER PRINT THIS
```

6. Configure your distribution in your CI Script or a selery.yml on top of your project. Simulation is set True by default. You will need the COINBASE TOKEN and SECRECT when setting Simulation to False in your selery.yml 


7. Run OpenSelery on the project folder you want to fund. This will send cryptocurrency to weighted random product contributors with a valid email address on the git platform or git commit: 

```bash
env $(cat ~/.openselery/tokens.env) ~/openselery/run.sh <target_directory>
```
8. You can integrate OpenSelery in your CI with the template yml file.
```
cat .github/actions/openselery.yml 
```

9. Get into [selery.py](selery.py)   

*Artwork by Miriam Winter*
