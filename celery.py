#!/usr/bin/python3
import subprocess
import argparse
import os
import json
import yaml
import re
import random
import sys

from opencelery.github_connector import GithubConnector
from opencelery.librariesio_connector import LibrariesIOConnector
from opencelery.coinbase_pay import CoinbaseConnector
from opencelery import gitremotes, celeryutils


# ArgumentParser

parser = argparse.ArgumentParser(description='opencelery - Automated Funding')
parser.add_argument("--folder", required=True, type=str,
                    help="Git folder to scan")

# Load default configs
# TODO: hacky solution - needs to be fixed
# If one variable is not found in the yml, all variables get defaults
try:
    default_config = yaml.safe_load(open('opencelery.yml'))
    include_dependencies = default_config['include_deps']
    include_self = default_config['include_self']
    # Is a relativ/median min contributions better as limit?
    min_contributions = default_config['min_contributions']
    dryrun = default_config['dryrun']
    check_equal_privat_and_public_wallet = default_config['check_equal_privat_and_public_wallet']
    include_tooling_and_runtime = default_config['include_tooling_and_runtime']

except:
    include_dependencies = True
    include_self = True
    min_contributions = 1
    dryrun = False

args = parser.parse_args()
git_folder = os.path.abspath(args.folder)

print("Working project path: \n{}".format(git_folder))
# Load parameters from environment variables
# Never print this enviorment variables since the print will keep forever in the Github CI Logs
libraries_api_key = os.environ['LIBRARIES_IO_TOKEN']
github_token = os.environ['GITHUB_TOKEN']
coinbase_token = os.environ['COINBASE_TOKEN']
coinbase_secret = os.environ['COINBASE_SECRET']

librariesIO = LibrariesIOConnector(libraries_api_key)
gitConnector = GithubConnector(github_token)
coinConnector = CoinbaseConnector(coinbase_token, coinbase_secret)

my_FUNDING = yaml.safe_load(open('FUNDING.yml'))
wallet_address = my_FUNDING['opencelery-bitcoin']

funding_emails = []
dependency_list = []
contributor_emails = []

if check_equal_privat_and_public_wallet:
    if not coinConnector.isWalletAddress(wallet_address):
        print("Wallet not found")
        sys.exit()
    else:
        print("FUNDING.yml Wallet matches coinbase wallet")

if include_self:
    # Find Official Repositories
    # Scan for Project Contributors
    target_remote = gitremotes.scanRemotes(git_folder, 'origin')
    project_id = gitConnector.getProjectID(target_remote)
    contributor_emails = gitConnector.getContributorInfo(project_id)

# Level 0 is the project itself.
# TODO: create data class for list items
    dependency_list.append({
            "platform": "", 
            "url": "",
            "project_id": project_id,
            "level": 0,
            "dependencies":[],
            "email_list": contributor_emails,
            })

if include_dependencies:
    # Scan for Dependencies Repositories
    # ToDo
    # Parse the json without local storage
    
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
    dependencies_json = celeryutils.getUniqueDependencies(dependencies_json)

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

            # Gather Project and User Information
            email_list = gitConnector.getContributorInfo(
                dependency["github_id"])
            dependency["email_list"] = email_list
            print("Emails for " + name)
            print("Number vaild emails entries:")
            print(len(email_list))
            dependency_list.append(dependency)

if include_tooling_and_runtime:
    pass

# Calculate Probability Weights
funding_emails, weights = celeryutils.getEmailsAndWeights(dependency_list) 
# Payout
n_funding_emails = 1 #number of possible funding emails
amount = '0.000002'
for i in range(n_funding_emails):
    if i >= len(funding_emails):
        break

    #pick a random contributor
    email = random.choices(funding_emails, weights, k=1)
    funding_emails.append(email[0])

    #remove contributor to avoid double funding for the same e-mail address
    weights.pop(funding_emails.index(email[0]))
    funding_emails.remove(email[0])

print(funding_emails)
print(weights)

for source in funding_emails:
    for user in funding_emails[0]:
        if not dryrun:
            receipt = coinConnector.payout(user['email'],amount)
            print(receipt)
            f = open("receipt.txt", "a")
            f.write(str(receipt))
            f.close()
        else:
            break
