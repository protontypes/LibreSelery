<img align="middle" src="./docs/design/OpenSelery-04.svg" width="512">     

> Software-Defined Funding Distribution

[![Actions Status](https://github.com/protontypes/openselery/workflows/openselery/badge.svg)](https://github.com/protontypes/openselery/actions)

Please consider openselery can payout all your cryptocurrency money if you configure it in this way.

## Contribution
Constributors on the 
master branch will probably get emails with cryptocurrency. Only git profiles with emails on the github profile page are considered. We will never send a URL in the note.

## Usage
Openselery is still not released and in experimental status.

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
```

6. Run on your target project folder. This will send cryptocurrency to weighted random product contributors with a valid email address on the git platform or git commit:    

```bash
env $(cat ~/.openselery/tokens.env | xargs) ~/openselery/run.sh <target_directory>
```

*Artwork by Miriam Winter*
