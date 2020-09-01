<img align="center" src="./docs/logo_LibreSelery-04.png" width="400">

### Continuous Funding

LibreSelery is a tool to distribute funding in free and open source projects. With a new funding model, it offers transparent, automated and adaptable compensation of contributors. The aim is to replace the middleman in donation distribution as far as possible with a free and transparent algorithm.

[![Join the chat at https://gitter.im/protontypes/LibreSelery](https://badges.gitter.im/protontypes/LibreSelery.svg)](https://gitter.im/protontypes/LibreSelery?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Docker Pulls](https://img.shields.io/docker/pulls/protontypes/libreselery)](https://hub.docker.com/r/protontypes/libreselery/tags)
[![stability-experimental](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/emersion/stability-badges#experimental)

*This project is funded by LibreSelery itself. If you contribute to this repository, you will receive a small amount from the pool to your public email address on GitHub.*

[![Actions Status](https://github.com/protontypes/libreselery/workflows/seleryaction/badge.svg)](https://github.com/protontypes/libreselery/actions?query=workflow%3Aseleryaction)
![Balance BTC](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/protontypes/libreselery/libreselery/balance_badge.json&style=flat&logo=bitcoin)
![Balance EUR](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/protontypes/libreselery/libreselery/native_balance_badge.json&style=flat&logo=bitcoin)
[![Donate with bitcoin](https://badgen.net/badge/Donate/3PVdiyLPR7MgaeFRJLW9mfuESZS2aAPX9w/orange?icon=bitcoin)](https://github.com/protontypes/libreselery/wiki/Donation)
[![Transaction History](https://badgen.net/badge/icon/Transaction%20History?icon=bitcoin&label)](https://github.com/protontypes/libreselery/wiki/Transaction-History)

## Concept

LibreSelery is a simple command line tool that runs upon any Github hosted project manually or automated by continuous integration. It works with a donation pool containing cryptocurrency in a wallet. With each run a small amount is taken from the donation pool and is distributed to the project's contributors and dependencies.

It is designed to run in a continuous integration pipeline like GitHub Actions. Donation transactions are automatically handled and transaction details are published for transparency into the wiki of your repository. Even the donation website is automatically created in your Wiki.

Donations are divided between contributors based on public and transparent metrics.
The metrics can be configured per repository and are based on the following weights:

- *Uniform Weight*: Everyone who contributed a minimum number of commits to the main branch is considered
- *Activity Weight*: Everyone who contributed in the last X commits
- *Service Weight*: Everyone who contributed to successful pull requests based on issues in the last X commits (not implemented yet [#132](https://github.com/protontypes/LibreSelery/issues/132))

The amount distributed to each contributor is calculated from an accumulation of these weights.
It is sent via the cryptocurrency market API to the public email address of the git platform user profile.
You can even configure the compensation of contributors from your own dependencies, therefore donating money back to open source platforms which play an integral role in your project.

The weights calculations are under active development and will be extended in the future in cooperation with the community. We are always open for concerns and are actively pursuing options for fair and considerate metrics regarding payout weights. The goal is to have a system which is fair and represents the contributions done but without prone to abuse.. 
Furthermore the issue of 'morality' is still open and any issues, concerns or ideas, regarding the following questions, are always welcome:

- What should give contributions more weight than others?" 
- How can we design metrics, which do represent and reward more helpful contributors?
- Feedback on how we can improve the metrics.

<p align="center"><img src="docs/concept.png"></p

## Implementation

LibreSelery ...

1. is configured based on the selery.yml file and runs as a GitHub Action on your project.
2. is triggered with every push on the main branch by the GitHub Action worflow file that is part of your project repository.
3. gathers contributor information about the target project via the GitHub and Libraries.io API.
4. filters out contributors with a hidden email address in the GitHub profile and below the minimum contribution limit. LibreSelery will not send emails to the git commit email addresses in order to avoid spam.
5. creates custom funding distribution weights based on the contribution rating of various projects: Minimum contribution, activity, ...
6. adds the weights to the combined weight used for different distribution splitting behaviors.
7. distributes the funding between the contributors based on the selected split behavior.
8. pays out cryptocurrency to the selected contributor's email addresses via the Coinbase API. Contributors without a Coinbase account will receive an email to claim the donation.
9. automatically generates a dotation and transaction visualization website in your GitHub wiki.


<a href="https://asciinema.org/a/353518">
<p align="center">
  <img src="https://asciinema.org/a/353518.svg" width="500">
</p></a>

## Features

* **Transparent** payout of GitHub project contributors with every push you make to your main (master) branch.
* Minimal changes to your GitHub project as shown in the [seleryexample](https://github.com/protontypes/seleryexample) to adapt LibreSelery with just a few steps.
* Detailed [transaction history](https://github.com/protontypes/libreselery/wiki/Transaction-History) is regenerated in your github wiki every time you run LibreSelery.
* **User defined payout configuration** by the [selery.yml](https://github.com/protontypes/libreselery/blob/master/selery.yml).
* Dependency scanning for most languages to **include developers of your dependencies** using [Libraries.io](https://libraries.io/).
* The money is distributed via Coinbase. Other payment methods like Uphold are currently work in progress.
* Donators can see transparent payout logs in [GitHub Action](https://github.com/protontypes/libreselery/actions?query=workflow%3Alibreselery).
* Self-hosted [donation website](https://github.com/protontypes/libreselery/wiki/Donation) for secure donations is automatically stored in the Wiki of your repository.
* Simulate the money distribution for your repository without actually transferring money to see how the money would be distributed.
* Automated statistic generation on how much money was paid out to which contributor.
* Splitting Strategies:
   - **full split** - All contributors receive a payout according to their weight.
   - **random split** - X contributors are randomly picked using the weight as probability.

<a href="https://asciinema.org/a/353518">

<p align="center">
  <img src="https://raw.githubusercontent.com/wiki/protontypes/libreselery/libreselery/transactions_per_user.png" width="500">
</p></a>

## Getting Started

Since the project is in its early stages the amount of funding on your wallet should therefore be limited.

### GitHub Actions Integration

Use the template [seleryaction](https://github.com/protontypes/seleryaction) to integrate LibreSelery into any GitHub project. Starting with GitHub Actions integration is the easiest way for newcomers and people without Linux knowledge.


### Command Line Usage

#### Running with Docker

1. Install [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04).
2. Clone LibreSelery and build your Container.
```bash
cd ~
git clone https://github.com/protontypes/libreselery.git
cd libreselery
docker build -t libreselery .
```
3. Create a token file for your user, where you store API keys and secrets.

```bash
mkdir -p ~/.libreselery/secrets ~/.libreselery/results/public
touch ~/.libreselery/secrets/tokens.env
```

4. LibreSelery just needs API tokens from [GitHub](https://github.com/settings/tokens) when `simulation = True` and `include_dependencies = False` in your `selery.yml`. The scope of your github token should not include any additional permissions beyond the standard minimum scope. Find out more about how to create GitHub tokens [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token). Replace XXXXX with the Coinbase and [Libraries.io](https://libraries.io/api) tokens to get started without creating an actual accounts for these APIs.


5. Make the token file read only.
```bash
chmod 400 ~/.libreselery/secrets/tokens.env
```

6. Clone your target repository.
```bash
git clone <target_repository>
```
7. Copy a [selery.yml](https://github.com/protontypes/seleryexample) into your <target_repository>.  Set `simulation: False` in your selery.yml to enable payouts with LibreSelery.
8. Adjust and test different configurations in simulation mode on your repository project.
9. Create a dedicated Coinbase account with limited amounts. Coinbase does not support sending emails to yourself. That's why you should use a dedicated email address when you are the owner of the Coinbase account and contributor of the project. Otherwise LibreSelery will skip these payouts.
10. Buy some cryptocurrency. See the [price list](https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/fees.html) for transferring money into the Coinbase account.
11. Configure the [access control settings](https://github.com/protontypes/libreselery/wiki/Coinbase-Token-API-Permission-for-LibreSelery) of the automated Coinbase wallet.
12. Never transfer or store large values with automated cryptocurrency wallets. Use [recurring automated buys](https://blog.coinbase.com/easier-recurring-buys-and-sells-on-coinbase-9a3cd7ea934e) to recharge you wallet on a regular base to avoid financial and security risks. Coinbase does not charge for transferring cryptocurrency from one Coinbase wallet to another.
13. Add your Coinbase API keys and secrets to the newly created file (`~/.libreselery/tokens.env`).  Never store these tokens in a public repository .

```bash
COINBASE_TOKEN=<your_coinbase_token>
COINBASE_SECRET=<your_coinbase_secret>
GITHUB_TOKEN=<your_github_tokens>
LIBRARIES_API_KEY=<your_libaries_io_tokens>
```
14. Send cryptocurrency to weighted random product contributors with a valid visible email address on GitHub:

```bash
env $(cat ~/.libreselery/secrets/tokens.env) ./run.sh <target_repository>
```

#### Run directly on your host machine

1. Install the Python and Ruby dependencies on your machine.

```bash
sudo apt update && sudo apt install git ruby ruby-dev curl python3-pip
```
2. Install LibreSelery and Python dependencies.

```bash
cd ~
git clone https://github.com/protontypes/libreselery.git
cd libreselery
pip3 install .
```

3. Ensure that `$HOME/.local/bin` is in `$PATH`. Check the output of `echo $PATH`. If it does not contain `.local/bin` add the following line to your dotfile for example `~/.bashrc`.

```bash
export PATH=$HOME/.local/bin:$PATH
```

4. Follow Step 3 to 14 of the [Running with Docker](Running-with-Docker) instructions. They should not differ at this steps.

5. Run LibreSelery on your target project and enjoy fresh Selery.

```bash
env $(cat ~/.libreselery/secrets/tokens.env) selery run -d ~/<target_repository> -r ~/.libreselery/results/
```


## Roadmap



<p align="center">
  <img src="https://github.com/protontypes/LibreSelery/wiki/roadmap.png" width="600">
</p></a>




LibreSelery is gone support multiple APIs and assets in the near future like:

- [x] GitHub
- [ ] Gitlab
- [ ] Savannah
- [x] Libraries.io
- [x] Coinbase
- [ ] Uphold



## Support LibreSelery

### Donations
Certainly we are funded by LibreSelery over direct donations via our [`donation website`](https://github.com/protontypes/libreselery/wiki/Donation). The usage and development of LibreSelery will always be free and without any charges. If you want to support us by using LibreSelery you need to add us to the [`tooling_repos.yml`](https://github.com/protontypes/seleryexample/blob/master/selery.yml).

### Contributions
Those who have contributed to the master branch receive emails with cryptocurrency from Coinbase. Only git profiles with emails on the GitHub profile page will be considered.
Find out more in the [contribution guide](https://github.com/protontypes/libreselery/wiki/Contribution-Guide) or look into the [good first issue]( https://github.com/protontypes/libreselery/labels/good%20first%20issue) labels to get into the project with some first simple tasks.

## Contact and Feedback
For further information please contact us at `team_at_protontypes.eu`, join our [Gitter chat](https://gitter.im/protontypes/libreselery) or check out our [wiki](https://github.com/protontypes/libreselery/wiki).

<p align="center">
  <img src="docs/selery_workflow.png" width="500">
</p>


*Artwork by Miriam Winter and [undraw](https://undraw.co/)*
