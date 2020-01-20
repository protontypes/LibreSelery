#!/usr/bin/python3
import subprocess
import argparse
import os
import json
import yaml
import re
import random
import sys

from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_pay import CoinbaseConnector
from openselery import gitremotes, seleryutils, calcweights

# argument parser for git project folder
parser = argparse.ArgumentParser(description='openselery - Automated Funding')
parser.add_argument("--folder", required=True, type=str,
                    help="Git folder to scan")
args = parser.parse_args()
git_folder = os.path.abspath(args.folder)
print("Working project path: \n{}".format(git_folder))

def ensureType(typ, config, field):
    result = config[field]
    if not(type(result) is typ):
        raise ValueError("Wrong Type in " + field + " expected " + str(typ) + " got: " + str(type(result)))
    return result

# load default configs
# if one variable is not found in the yml, all variables get defaults.
try:
    config = yaml.safe_load(open('openselery.yml'))
    dryrun = ensureType(bool, config, 'dryrun')
    include_dependencies = ensureType(bool, config, 'include_deps')
    include_self = ensureType(bool, config, 'include_self')
    include_tooling_and_runtime = ensureType(bool, config, 'include_tooling_and_runtime')
    # Is a relativ/median min contributions better as limit?
    min_contributions = ensureType(int, config, 'min_contributions')
    check_equal_privat_and_public_wallet = ensureType(bool, config, 'check_equal_privat_and_public_wallet')
    skip_email = ensureType(bool, config, 'skip_email')
    btc_per_transaction = ensureType(float, config, 'btc_per_transaction')
    selected_contributor = ensureType(int, config, 'selected_contributor')
    total_payout_per_run = ensureType(float, config, 'total_payout_per_run')
    if not total_payout_per_run/selected_contributor == btc_per_transaction:
        raise ValueError("Payout values do not match")
    print("Reading openselery.yml completed")
    print(config)

except ValueError as err:
    dryrun = True
    include_dependencies = False
    include_self = True
    include_tooling_and_runtime = False
    min_contributions = 1
    check_equal_privat_and_public_wallet = True
    skip_email = True
    btc_per_transaction = 0.000002
    selected_contributor = 1
    total_payout_per_run = 0.000002
    print(err)
    print("Could not read openselery.yml. \nUse default config")


# load parameters from environment variables
# never print this
# TODO: check if user input is sane
libraries_api_key = os.environ['LIBRARIES_IO_TOKEN']
github_token = os.environ['GITHUB_TOKEN']
coinbase_token = os.environ['COINBASE_TOKEN']
coinbase_secret = os.environ['COINBASE_SECRET']

# establish connection to used restapi services
librariesIO = LibrariesIOConnector(libraries_api_key)
gitConnector = GithubConnector(github_token)
coinConnector = CoinbaseConnector(coinbase_token, coinbase_secret)

my_FUNDING = yaml.safe_load(open('FUNDING.yml'))
wallet_address = ensureType(str,my_FUNDING,'openselery-bitcoin')

if check_equal_privat_and_public_wallet:
    #Check if the public wallet is hold by the secret tokens account 
    if not coinConnector.isWalletAddress(wallet_address):
        print("Wallet not found")
        sys.exit()
    else:
        print("FUNDING.yml Wallet matches coinbase wallet")

funding_emails = []
project_list = []
contributor_emails = []
selery_emails = []

if include_self:
    # find official repositories
    # scan for project contributors
    target_remote = gitremotes.scanRemotes(git_folder, 'origin')
    project_id = gitConnector.getGithubID(target_remote)
    contributor_emails = gitConnector.getContributorInfo(project_id)

    # Level 0 is the project itself.
    project_list.append({
            "platform": "",
            "url": "",
            "project_id": project_id,
            "level": 0,
            "dependencies":[],
            "email_list": contributor_emails,
            })

if include_dependencies:
    # scan for dependencies repositories
    run_path = os.path.dirname(os.path.realpath(__file__))
    process = subprocess.run(['ruby', run_path+'/scripts/scan.rb', '--project='+git_folder],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    process.stdout
    if process.returncode == 0:
        dependencies_json = json.loads(process.stdout)
    else:
        print("Can not find project manifesto")
        print(process.stderr)
        exit()
    print('dependencies json:')
    print(dependencies_json)
    dependencies_json = seleryutils.getUniqueDependencies(dependencies_json)

    for platform_name in dependencies_json.keys():
        if not dependencies_json[platform_name]:
            continue
        for deps in dependencies_json[platform_name]:
            name = deps["name"]
            dependency = {"platform": platform_name, "name": name, "level": 1}
            ownerandproject = librariesIO.getOwnerandProject(
                platform_name, name)
            if not ownerandproject:
                continue
            depData = librariesIO.getDependencyData(
                ownerandproject["owner"], ownerandproject["project_name"])
            if not depData:
                continue
            dependency["dependencies"] = depData["dependencies"]
            dependency["github_id"] = depData["github_id"]

            # gather project and user information
            email_list = gitConnector.getContributorInfo(
                dependency["github_id"])
            dependency["email_list"] = email_list
            print("Emails for " + name)
            print("Number vaild emails entries:")
            print(len(email_list))
            project_list.append(dependency)

print(project_list)

if include_tooling_and_runtime:
    pass

# calculate probability weights
funding_emails, weights = calcweights.getEmailsAndWeights(project_list)
print(funding_emails)
# payout
for i in range(int(selected_contributor)):
    if i >= len(funding_emails[0]):
        break

    email = random.choices(funding_emails[0], weights, k=1)
    selery_emails.append(email[0])

print(weights)
print(selery_emails)

for contributor in selery_emails:
    if not dryrun:
         receipt = coinConnector.payout(contributor['email'], btc_per_transaction, skip_email)
         print(receipt)
         f = open("receipt.txt", "a")
         f.write(str(receipt))
         f.close()
    else:
         break
