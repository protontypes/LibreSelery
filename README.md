<img align="middle" src="./docs/design/OpenSelery-04.svg" width="512">     

> Software Defined Funding

[![Actions Status](https://github.com/protontypes/openselery/workflows/openselery/badge.svg)](https://github.com/protontypes/openselery/actions)

Please consider openselery can payout all your cryptocurrency money if you configure it in this way.

## Contribution
Constributors on the 
master branch will probably get emails with cryptocurrency. Only git profiles with emails on the github profile page are considered. We will never send a URL in the note.

## Usage
Openselery is still not released and in experimental status.

1. Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

```bash
git clone https://github.com/openselery/openselery.git
cd openselery
bash ./install_and_build.sh
```

2. Create a dedicated coinbase account with limited amounts. 
3. Never transfer or store large values with automated cryptocurrency wallets. Use recurring automated transaction from another account to recharge you wallet on a regular base. 
4. Transfer some money to this wallet for testing Openselery.  
5. Add your tokens from the coinbase API:      

```bash
nano ~/.openselery/tokens.env
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

6. Run openselery on your target project root folder. This will send cryptocurrency to a weighted random product contributor with an email address on the git platform or git commit:    

```bash
bash openselery_docker.sh ~/gitclones/<target_projects>
```

7. For openselery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.openselery/tokens.env | xargs) ~/openselery/selery.py --project=$PROJECT_DIR_TO_SCAN
```
