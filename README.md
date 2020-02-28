<img align="middle" src="./docs/design/OpenSelery-04.png" width="400"> 

> Software Defined Funding Distribution

[![Actions Status](https://github.com/protontypes/openselery/workflows/openselery/badge.svg)](https://github.com/protontypes/openselery/actions)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/openselery/openselery)                               
[![Donate with Ethereum](https://en.cryptobadges.io/badge/small/0x187cC0D89078Cd6177a1A8Fe7DE04388ECCc4029)](https://en.cryptobadges.io/donate/0x187cC0D89078Cd6177a1A8Fe7DE04388ECCc4029)           
[![Balance](https://img.balancebadge.io/eth/0x187cC0D89078Cd6177a1A8Fe7DE04388ECCc4029.svg)](https://img.balancebadge.io/eth/0x187cC0D89078Cd6177a1A8Fe7DE04388ECCc4029.svg)           

* [Project Slides](http://protontypes.eu/)
* [Roadmap](https://github.com/protontypes/openselery/wiki)
* [Knowledge-Links](https://github.com/protontypes/openselery/wiki/Knowledge-Links)

> Please keep in mind that OpenSelery is in an experimental state. The amount of funding should therefore be kept to a minimum. OpenSelery is not unit tested yet.

## Contribution
Constributors on the master branch will probably get emails with cryptocurrency. Only git profiles with emails on the Github profile page are considered. We will never send a URL in the note.

## Usage
### Command-Line Tool
1. The [Gitub](https://github.com/settings/tokens) and [Libraries.io](https://libraries.io/api) tokens are easy to obtain. Simulate payouts without the [coinbase token](https://www.coinbase.com/settings/api) to find the right settings. Configure the [access control settings](https://github.com/protontypes/openselery/wiki/Coinbase-Settings) of the automated coinbase account.

2. Install with [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/):

  ```bash
  cd ~
  git clone https://github.com/openselery/openselery.git
  cd openselery
  ./build.sh
  ```

3. Create a dedicated coinbase account with limited amounts. OpenSelery is based on the APIs of The Libraries.io, Github and Coinbase. To provide service you need create to tokens in the corresponding accounts. Setting simulation to false will require your coinbase tokens.

4. Never transfer or store large values with automated cryptocurrency wallets. Use recurring automated transaction from another account to recharge you wallet on a regular base. 

5. Transfer some money to this wallet for testing. See the [price list](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/fees.html) for transfering money to the coinbase account.

6. Create a read only token file for your user:

  ```bash
  mkdir ~/.openselery/
  touch ~/.openselery/tokens.env
  chmod 400 ~/.openselery/tokens.env
  ```


7. Add your tokens API keys to the local file: 

  ```bash
  nano ~/.openselery/tokens.env

  COINBASE_TOKEN=XXXXXXXXXXXXXXXX
  COINBASE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  LIBRARIES_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  ```

8. Configure your distribution in the `selery.yml` in root of your target project. `simulation` is set `True` by default. You will need `COINBASE_TOKEN` and `COINBASE_SECRET` when setting Simulation to False in your selery.yml 


9. Run OpenSelery on the project folder you want to fund. This will send cryptocurrency to weighted random product contributors with a valid email address on the git platform or git commit: 

  ```bash
  env $(cat ~/.openselery/tokens.env) ~/openselery/run.sh <target_directory>
  ```

### Continuous Integration  
1. Add the token of libraries.io and coinbase to your [secrets](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets).

2. You can integrate OpenSelery in your CI by copying the `openselery.yml` file in your `.github/actions/` destination project directory. Check the setting before appling to your CI Pipeline:

  ```
  cat .github/actions/openselery.yml 
  ```
3. Set the simulation parameter `False` and `COINBASE_LIVE` environment variable to `True`.

4. Depending on the `openselery.yml` a payout will be triggered. The default setting runs OpenSelery with every new version of the destination project. 

5. Protect your master branch in the Github Setting under 'Branches'. Activate the 'Restrict who can push to matching branches' option. 


Get into [selery.py](selery.py)   

  *Artwork by Miriam Winter*
