# Protontypes

[GitHub Terms of Service](https://help.github.com/en/github/site-policy/github-terms-of-service#h-api-terms): 
> You may not use the API to download data or Content from GitHub for spamming purposes, including for the purposes of selling GitHub users' personal information, such as to recruiters, headhunters, and job boards.


## Usage

Install with docker:

```bash
git clone https://github.com/protontypes/protontypes.git
cd protontypes
bash ./build_docker.sh
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

For usage of protontypes without docker you can load the tokens into your base environment:

```bash
env $(cat ~/.protontypes/tokens.env | xargs) ~/protontypes/main.py --project=$PROJECT_DIR_TO_SCAN
```
