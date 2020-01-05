 

# OpenCelery <img align="middle" src="./docs/celery_logo.svg" width="128"> [![Actions Status](https://github.com/protontypes/opencelery/workflows/docker_run/badge.svg)](https://github.com/protontypes/opencelery/actions)    
> Invest straight into your software.

## Usage

Install with docker:

```bash
git clone https://github.com/opencelery/opencelery.git
cd opencelery
bash ./install_and_build.sh
```
__Use only automated wallets with limited amounts since opencelery is still not released.__       
Add the tokens to tokens.env file:

```bash
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Run opencelery on your target project root folder:

```bash
bash opencelery_docker.sh ~/gitclones/<target_projects>
```

For usage of opencelery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.opencelery/tokens.env | xargs) ~/opencelery/celery.py --project=$PROJECT_DIR_TO_SCAN
```
