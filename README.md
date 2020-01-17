<img align="middle" src="./docs/opencelery-05.svg" width="128">  
> Self-sustain your git repository

[![Actions Status](https://github.com/protontypes/opencelery/workflows/opencelery/badge.svg)](https://github.com/protontypes/opencelery/actions)

Please consider OpenCelery can payout all your cryptocurrency money if you configure it in this way.

## Contribution
Constributors on the master branch will probably get emails with cryptocurrency. Only git profiles with emails on the github profile page are considered. We will never send a URL in the note.

## Usage
OpenCelery is still not released and in experimental status.

1. Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

```bash
git clone https://github.com/opencelery/opencelery.git
cd opencelery
bash ./install_and_build.sh
```

2. Create a dedicated coinbase account with limited amounts. 
3. Never transfer or store large values with automated cryptocurrency wallets. Use recurring automated transaction from another account to recharge you wallet on a regular base. 
4. Transfer some money to this wallet for testing OpenCelery.  
5. Add your tokens from the coinbase API:      

```bash
nano ~/.opencelery/tokens.env
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

6. Run opencelery on your target project root folder. This will send cryptocurrency to a weighted random product contributor with an email address on the git platform or git commit:    

```bash
bash opencelery_docker.sh ~/gitclones/<target_projects>
```

7. For opencelery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.opencelery/tokens.env | xargs) ~/opencelery/celery.py --project=$PROJECT_DIR_TO_SCAN
```
