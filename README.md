# OpenCelery <img src="./docs/celery_logo.svg" width="128">  
> Fund people in your git project.

[![Actions Status](https://github.com/protontypes/opencelery/workflows/docker_run/badge.svg)](https://github.com/protontypes/opencelery/actions)  
## Usage
OpenCelery is still not released and in experimental status.

1. Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

```bash
git clone https://github.com/opencelery/opencelery.git
cd opencelery
bash ./install_and_build.sh
```
2. Create a dedicated new wallet with limited amounts.            
3. Transfer some money to this wallet for testing OpenCelery.  
4. Add the tokens to tokens.env file:      

```bash
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

5. Run opencelery on your target project root folder.      
**This will send cryptocurrency to a weighted random product contributor with an email address on the git platform or git commit.**    

```bash
bash opencelery_docker.sh ~/gitclones/<target_projects>
```

6. For usage of opencelery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.opencelery/tokens.env | xargs) ~/opencelery/celery.py --project=$PROJECT_DIR_TO_SCAN
```
