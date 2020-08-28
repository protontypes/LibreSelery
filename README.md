<img align="middle" src="./docs/OpenSelery-04.png" width="400">

### Continuous Funding

OpenSelery is a tool to distribute funding in free and open source projects. With a new funding model it offers transparent, automated and adaptable compensation of contributors. The aim is to replace the middleman of donation distribution as far as possible with a free and transparent algorithm.

*This project is funded by OpenSelery itself. If you contribute to this repository, you will immediately receive donation for this project.*

[![](https://img.shields.io/gitter/room/protontypes/openselery)](https://gitter.im/protontypes/openselery) 
[![](https://img.shields.io/docker/cloud/build/protontypes/openselery?logo=docker)](https://hub.docker.com/r/openselery/openselery) 
[![stability-experimental](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/emersion/stability-badges#experimental)   

[![Actions Status](https://github.com/protontypes/openselery/workflows/seleryaction/badge.svg)](https://github.com/protontypes/openselery/actions?query=workflow%3Aseleryaction)
![Balance](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/balance_badge.json&style=flat&logo=bitcoin)
![Balance](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/native_balance_badge.json&style=flat&logo=bitcoin)      
[![Donate with bitcoin](https://badgen.net/badge/Donate/3PVdiyLPR7MgaeFRJLW9mfuESZS2aAPX9w/orange?icon=bitcoin)](https://github.com/protontypes/openselery/wiki/Donation)
[![Transaction History](https://badgen.net/badge/icon/Transaction%20History?icon=bitcoin&label)](https://github.com/protontypes/openselery/wiki/Transaction-History)

## Concept

Donations are collected in a Cryptocurrency wallet (currently Bitcoin) that acts as a donation pool.
At each run an amount is taken from the donation pool and distributed to the project's contributors and dependencies.

It is designed to run in a continuous integration pipeline like GitHub Actions. Donation transactions are automatically handled and transaction details are published for transparency into the wiki of your repository.

Donations are divided between contributors based on a public and transparent metric.
The metric can be configured per repository and is based on the following weights:

- *Uniform Weight*: Everyone who contributed a minimum number of commits to the main branch is considered
- *Activity Weight*: Everyone who contributed in the last X commits
- *Service Weight*: Everyone who is part of the uniform weight contributed to an closed issue in the last X commits (not implemented yet)

More weights are under active development and will be added in the future. 

The amount distributed to each contributor is calculated from an accumulation of these weights.
It is sent via the cryptocurrency market API to the public email address of the git platform user profile.
You can even activate to compensate contributors from your dependencies.

<p align="center"><img src="docs/concept.png"></p>

## Implementation

OpenSelery ...


1. is configured based on the selery.yml file and runs as a Github Action on your project.
2. is triggered with every push on the main branch by the Github Action worflow file that is part of your project repository.
3. gathers contributor information about the target project via the Github and Libraries.io API.
4. filters out contributors with a hidden email address in the github profile and below the minimum contribution limit. OpenSelery will not send emails to the git commit email addresses in order to avoid spam.
5. creates custom funding distribution weights based on the contribution rating of various projects: Minimum contribution, activity, ...
6. adds the weights to the combined weight used for different distribution splitting behaviors.
7. distributes the funding between the contributors based on the selected split behavior.
8. pays out cryptocurrency to the selected contributors' email addresses via the Coinbase API. Contributors without a Coinbase account will receive an email to claim the donation.
9. generates automatically a dotation and transaction visualization website in your Github wiki.


<a href="https://asciinema.org/a/353518">
<p align="center">
  <img src="https://asciinema.org/a/353518.svg" width="500">
</p></a>

## Features

* **Transparent** payout of Github project contributors with every push you make to your main (master) branch.
* Minimal changes to your Github project shown in the [`seleryexample`](https://github.com/protontypes/seleryexample) to adapt OpenSelery with just a view steps.
* Detailed [`transaction history`](https://github.com/protontypes/openselery/wiki/Transaction-History) is regenerated in your github wiki every time you run OpenSelery.
* **User defined payout configuration** by the [`selery.yml`](https://github.com/protontypes/openselery/blob/master/selery.yml).
* Dependency scanning for most languages to **even include developers of your dependencies** using [`Libraries.io`](https://libraries.io/).
* The money is distributed via Coinbase. Other payment methods like Uphold are currently work in progress.
* Donators can see transparent payout logs in the [`public Github Action`](https://github.com/protontypes/openselery/actions?query=workflow%3Aopenselery).
* Self-hosted [`Donation Website`](https://github.com/protontypes/openselery/wiki/Donation) for secure donations is automatically stored in the Wiki of your repository.
* Simulate the money distribution for your repository without actually transferring money to see how the money would be distributed.
* Automated statistic generation on how much money was paid out to which contributor.
* Splitting Strategies:
   - full_split - All contributors receive a payout according to their weight.
   - random_split - X contributors are randomly picked using the weight as probabilty.

<a href="https://asciinema.org/a/353518">

<p align="center">
  <img src="https://raw.githubusercontent.com/wiki/protontypes/openselery/openselery/transactions_per_user.png" width="500">
</p></a>

## Getting Started

Since the project is in its early stages the amount of funding on your wallet should therefore be limited.

### Github Actions Integration

Use the [template](https://github.com/protontypes/seleryexample) to integrate OpenSelery into any GitHub project. Running OpenSelery with GitHub Actions is the easiest way for newcomers and people without Linux knowledge.


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
```bash
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
12. Add your coinbase API keys and secrets to the newly created file (`~/.openselery/tokens.env`).  Never store these tokens in a public repository .

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
pip3 install .
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

OpenSelery plans to support multiple APIs and assets in the near future like:
- [x] Github
- [ ] Gitlab
- [ ] Savannah
- [x] Libraries.io
- [x] Coinbase
- [ ] Uphold



## Support OpenSelery

### Donations
Certainly we are funded by OpenSelery over direct donations via our [`Donation Website`](https://github.com/protontypes/openselery/wiki/Donation). The usage and development of OpenSelery will always be free and without any charges. If you want to support us by using OpenSelery you need to add us to the [`tooling_repos.yml`](https://github.com/protontypes/seleryexample/blob/master/selery.yml).

### Contributions
Those who have contributed to the master branch receive emails with cryptocurrency from Coinbase. Only git profiles with emails on the GitHub profile page will be considered.
Find out more in the [Contribution Guide](https://github.com/protontypes/openselery/wiki/Contribution-Guide) or look into the [Good First Issue]( https://github.com/protontypes/openselery/labels/good%20first%20issue) labels to get into the project with some first simple tasks.

## Contact and Feedback
For further information please contact us at`team_at_protontypes.eu`, join our [Gitter Chat](https://gitter.im/protontypes/openselery) or check out our [Wiki](https://github.com/protontypes/openselery/wiki).

<p align="center">
  <img src="docs/selery_workflow.png" width="500">
</p>


*Artwork by Miriam Winter and [undraw](https://undraw.co/)*
