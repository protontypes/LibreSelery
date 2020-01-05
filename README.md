# opencelery [![Actions Status](https://github.com/opencelery/opencelery/workflows/docker_run/badge.svg)](https://github.com/opencelery/opencelery/actions)

Software is made out of humans. Invest straight into them.

## Usage

Install with docker:

```bash
git clone https://github.com/opencelery/opencelery.git
cd opencelery
bash ./install_and_build.sh
```

Add the tokens to tokens.env file:

```bash
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Run opencelery on your target project root folder:

```bash
bash opencelery_docker ~/gitclones/<target_projects>
```

For usage of opencelery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.opencelery/tokens.env | xargs) ~/opencelery/main.py --project=$PROJECT_DIR_TO_SCAN
```
