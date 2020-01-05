# opencelery [![Actions Status](https://github.com/OpenCelery/OpenCelery/workflows/docker_run/badge.svg)](https://github.com/OpenCelery/OpenCelery/actions)

Software is made out of humans. Invest straight into them.

## Usage

Install with docker:

```bash
git clone https://github.com/OpenCelery/OpenCelery.git
cd OpenCelery
bash ./install_and_build.sh
```

Add the tokens to tokens.env file:

```bash
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Run OpenCelery on your target project root folder:

```bash
bash OpenCelery_docker ~/gitclones/<target_projects>
```

For usage of OpenCelery without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.OpenCelery/tokens.env | xargs) ~/OpenCelery/main.py --project=$PROJECT_DIR_TO_SCAN
```
