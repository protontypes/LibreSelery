# Protontypes [![Actions Status](https://github.com/protontypes/protontypes/workflows/docker_run/badge.svg)](https://github.com/protontypes/protontypes/actions)

Software is made out of humans. Invest straight into them.

## Usage

Install with docker:

```bash
git clone https://github.com/protontypes/protontypes.git
cd protontypes
bash ./install_and_build.sh
```

Add the tokens to tokens.env file:

```bash
COINBASE_TOKEN=XXXXXXXXXXXXXXXX
COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
LIBRARIES_IO_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Run protontypes on your target project root folder:

```bash
bash protontypes_docker ~/gitclones/<target_projects>
```

For usage of protontypes without docker you can load the tokens into your base environment (insecure):

```bash
env $(cat ~/.protontypes/tokens.env | xargs) ~/protontypes/main.py --project=$PROJECT_DIR_TO_SCAN
```
