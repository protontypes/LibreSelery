# OpenCelery <img align="middle" src="./docs/celery_logo.svg" width="128">  
> Fund people in your git project.

[![Actions Status](https://github.com/protontypes/opencelery/workflows/docker_run/badge.svg)](https://github.com/protontypes/opencelery/actions)  
## Usage

> Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

```bash
git clone https://github.com/opencelery/opencelery.git
cd opencelery
bash ./install_and_build.sh
```
> Create a dedicated new wallet with limited amounts since OpenCelery is still not released and in experimental status.       
> Transfer some money to this wallet for testing OpenCelery.      
> Add the tokens to tokens.env file:      

```bash
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

> Run opencelery on your target project root folder.      
> This will send cryptocurrency to a weighted random product contributor with an email address on the git platform or git commit.    

```bash
bash opencelery_docker.sh ~/gitclones/<target_projects>
```

> For usage of opencelery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.opencelery/tokens.env | xargs) ~/opencelery/celery.py --project=$PROJECT_DIR_TO_SCAN
```
