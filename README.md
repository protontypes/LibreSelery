 

# OpenCelery <img align="middle" src="./docs/celery_logo.svg" width="128"> 

[![Actions Status](https://github.com/protontypes/opencelery/workflows/docker_run/badge.svg)](https://github.com/protontypes/opencelery/actions)   

> Fund all the humans in your git project

## Usage

Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

```bash
git clone https://github.com/opencelery/opencelery.git
cd opencelery
bash ./install_and_build.sh
```
Create a new celery wallet with limited amounts since OpenCelery is still not released.
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
