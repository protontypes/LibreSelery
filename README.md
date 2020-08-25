<img align="middle" src="./docs/OpenSelery-04.png" width="400">

### Continuous Software Funding

OpenSelery is a tool to distribute funding in free and open source projects. With a new funding model it offers transparent, automated and adaptable compensation of contributors.

*This project is funded by its own solution. If you contribute to this repository, you will immediately earn money.*

[![](https://img.shields.io/gitter/room/protontypes/openselery)](https://gitter.im/protontypes/openselery) 
[![](https://img.shields.io/docker/cloud/build/protontypes/openselery?logo=docker)](https://hub.docker.com/r/openselery/openselery) 
[![stability-experimental](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/emersion/stability-badges#experimental)   

[![Actions Status](https://github.com/protontypes/openselery/workflows/seleryaction/badge.svg)](https://github.com/protontypes/openselery/actions?query=workflow%3Aseleryaction)
![Balance](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/balance_badge.json&style=flat&logo=bitcoin)
![Balance](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/native_balance_badge.json&style=flat&logo=bitcoin)      
[![Donate with bitcoin](https://badgen.net/badge/Donate/3PVdiyLPR7MgaeFRJLW9mfuESZS2aAPX9w/orange?icon=bitcoin)](https://github.com/protontypes/openselery/wiki/Donation)
[![Transaction History](https://badgen.net/badge/icon/Transaction%20History?icon=bitcoin&label)](https://github.com/protontypes/openselery/wiki/Transaction-History)

## Concept


OpenSelery is a donation distribution system for free and open source projects.
Donations are collected in a Bitcoin wallet that acts as a donation pool.
At each run, a constant amount of money is taken from the donation pool and distributed to the project's donors.
It runs in continuous integration pipelines like GitHub Actions.

OpenSelery is different from other funding solutions in a very essential way.
**Money flows directly from the donors to the contributors of the project, without any middlemen.**
Donation transactions are automatically handled by the continuous integration.
Transaction details are published for transparency into the wiki of your repository.

The distribution is triggered by every push to your main branch.
The money is then split between contributors based on a public and transparent metric.
The metric can be configured per repository and is based on the following weights:

- *Uniform Weight*: Everyone who contributed a minimum number of commits to the main branch is considered
- *Activity Weight*: Everyone who contributed in the last X commits
- *Service Weight*: Everyone who is part of the uniform weight contributed to an closed issue in the last X commits (not implemented yet)

More weights are under consideration.
It is a difficult and controversial topic, since the importance and amount of contributions cannot be measured in perfectly fair way.

The amount distributed to each contributor is calculated from a sum of these weights.
The money is sent via the Coinbase API to the public email address on the contributor's GitHub profile.
We won't send emails to the git commit email addresses in order not to spam anyone.
You can even activate to compensate contributors from your dependencies.

## How it works

1. OpenSelery is configured based on the selery.yml file and runs as a Github Action in your project.
2. Is triggered with every push on the main branch.
3. Gathers contributor information about the target project via the Github and Libraries.io API.
4. Filters out contributors with a hidden email address in the github profile and below the minimum contribution limit
5. Creates custom funding distribution weights based on the contribution rating of various projects: Minimum contribution, activity, ...
6. Adds the weights to the combined weight used for different distribution modes
7. Distributes the funding between the contributors based on the selected mode.
8. Pay out cryptocurrency to the selected contributors' email addresses via the Coinbase API. Contributors without a Coinbase account will receive an email to claim the donation.


<a href="https://asciinema.org/a/353518">
<p align="center">
  <img src="https://asciinema.org/a/353518.svg" width="500">
</p></a>

## Features

* **Transparent payout** of Github project contributors with every push you make to your main (master) branch.
* Minimal changes to your Github project shown in the [`seleryexample`](https://github.com/protontypes/seleryexample) to adapt OpenSelery with just a view steps.
* Detailed [`transaction history`](https://github.com/protontypes/openselery/wiki/Transaction-History) is regenerated in your github wiki every time you run OpenSelery.
* **User defined payout configuration** by the [`selery.yml`](https://github.com/protontypes/openselery/blob/master/selery.yml).
* Dependency scanning for most languages to **even include developers of your dependencies** using [`Libraries.io`](https://libraries.io/).
* The money is distributed via Coinbase. Other payment methods like Paypal or Uphold will be considered.
* Donators can see transparent payout logs in the [`public Github Action`](https://github.com/protontypes/openselery/actions?query=workflow%3Aopenselery).
* Self-hosted [`QR code`](https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/wallet_qrcode.png) for secure donations is automatically stored in the Wiki of your repository.
* Simulate the money distribution for your repository without actually transferring money to see how the money would be distributed.
* Automated statistic generation on how much money was paid out to which contributor.


<a href="https://asciinema.org/a/353518">
<p align="center">
  <img src="https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/transactions_per_user.png" width="500">
</p></a>

## Getting Started

**Since the project is in its early stages the amount of funding on your wallet should therefore be limited.**

### Github Actions Integration

Use the [template](https://github.com/protontypes/seleryexample) to integrate OpenSelery into any GitHub project.
**Running OpenSelery with GitHub Actions is the easiest way for newcomers and people without Linux knowledge.**



### Command Line Usage

#### Running with Docker

1. Install [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04):
```bash
cd ~
git clone https://github.com/protontypes/openselery.git
cd openselery
./build.sh
```
2. Create a token file for your user, where you store API keys and secrets:

```bash
mkdir -p ~/.openselery/secrets ~/.openselery/results/public
touch ~/.openselery/secrets/tokens.env
```

3. OpenSelery just needs API tokens from [Github](https://github.com/settings/tokens) when `simulation = True` and `include_dependencies = False` in your `selery.yml`. The scope of your github token should not include any additional permissions beyond the standard minimum scope. Find out more about how to create Github tokens [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token). Replace XXXXX with the Coinbase and [Libraries.io](https://libraries.io/api) tokens to get started without creating an actual accounts for these APIs.


4. Make the token file read only:
```
chmod 400 ~/.openselery/secrets/tokens.env
```

5. Clone your target repository:
```bash
git clone <target_repository>
```
6. Copy a [selery.yml](https://github.com/protontypes/seleryexample) into your <target_repository>.  Set `simulation: False` in your selery.yml to enable payouts with OpenSelery.
7. Adjust and test different configurations in simulation mode on your repository project.
8. Create a dedicated Coinbase account with limited amounts. Coinbase does not support sending emails to yourself. That's why you should use a dedicated email address when you are the owner of the Coinbase account and contributor of the project. Otherwise OpenSelery will skip these payouts.
9. Buy some cryptocurrency. See the [price list](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/fees.html) for transferring money into the Coinbase account.
10. Configure the [access control settings](https://github.com/protontypes/openselery/wiki/Coinbase-Settings) of the automated Coinbase wallet.  
11. Never transfer or store large values with automated cryptocurrency wallets. Use [recurring automated buys](https://blog.coinbase.com/easier-recurring-buys-and-sells-on-coinbase-9a3cd7ea934e) to recharge you wallet on a regular base to avoid financial and security risks. Coinbase does not charge for transferring cryptocurrency from one Coinbase wallet to another.
12. Add your coinbase API keys and secrets to the newly created file (`~/.openselery/tokens.env`). **Never store these tokens in a public repository**.

```bash
COINBASE_TOKEN=<your_coinbase_token>
COINBASE_SECRET=<your_coinbase_secret>
GITHUB_TOKEN=<your_github_tokens>
LIBRARIES_API_KEY=<your_libaries_io_tokens>
```
13. Send cryptocurrency to weighted random product contributors with a valid visible email address on GitHub:

```bash
env $(cat ~/.openselery/secrets/tokens.env) ./run.sh <target_repository>
```

#### Run directly on your host machine

1. Install the dependencies on your machine.

```bash
sudo apt update && sudo apt install git ruby ruby-dev curl python3-pip
python3 setup.py install --user
```

2. Ensure that `$HOME/.local/bin` is in `$PATH`. Check the output of `echo $PATH`. If it does not contain `.local/bin` add the following line to your dotfile for example `~/.bashrc`.

```bash
export PATH=$HOME/.local/bin:$PATH
```

3. Run OpenSelery on your target project.

```bash
env $(cat ~/.openselery/secrets/tokens.env) selery run -d ~/<target_repository> -r ~/.openselery/results/
```


## API Integrations

OpenSelery plans to support multiple APIs and assets in the near future:
- [x] Github
- [x] Libraries.io
- [ ] Gitlab
- [x] Coinbase
- [ ] Paypal (Already tested but requires a business account activation [#34](https://developer.paypal.com/docs/api/overview/#))
- [ ] Uphold



## Support OpenSelery

### Donations

Certainly we are funded by OpenSelery over direct donations via our [`QR code`](https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/wallet_qrcode.png). The usage and development of OpenSelery will always be free and without any charges. If you want to support us by using OpenSelery you need to add us to the [`tooling_repos.yml`](https://github.com/protontypes/seleryexample/blob/master/selery.yml).

### Contributions

Those who have contributed to the master branch receive emails with cryptocurrency from Coinbase. Only git profiles with emails on the GitHub profile page will be considered.
Find out more in the [Design Guidelines](https://github.com/protontypes/openselery/wiki/Design-Guidelines) or look into the [Good First Issue]( https://github.com/protontypes/openselery/labels/good%20first%20issue) labels to get into the project.

## Contact and Feedback
For further information please contact us at`team_at_protontypes.eu`, join our [Gitter Chat](https://gitter.im/protontypes/openselery) or check out our [Wiki](https://github.com/protontypes/openselery/wiki).

<p align="center">
  <img src="docs/selery_workflow.png" width="500">
</p>


*Artwork by Miriam Winter and [undraw](https://undraw.co/)*
