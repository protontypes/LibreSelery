# Protontypes

## Usage

Install with docker:

```bash
git clone https://github.com/protontypes/protontypes.git
cd protontypes
bash ./build_docker.sh
```

Create the tokens file:

```bash
mkdir ~/.protontypes/
cd ~/.protontypes/
touch tokens.env
# Remove read permission for all other users
sudo chmod u=rw,g-rwx,o-rwx ~/.protontypes/token.env
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
bash protontypes_dockerized ~/gitclones/<target_project>
```

For usage of protontypes without docker you can load the tokens into your base environment:

```bash
env $(cat ~/.protontypes/tokens.env | xargs) ~/protontypes/protontypes.py --project ~/gitclones/
```

