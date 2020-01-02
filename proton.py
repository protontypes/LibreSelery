#!/usr/bin/python3
import subprocess
import argparse
import os
import json
import re
import random

from protontypes.github_connector import GithubConnector
from protontypes.librariesio_connector import LibrariesIOConnector
from protontypes.coinbase_pay import CoinbaseConnector
from protontypes import gitremotes,protonutils

parser = argparse.ArgumentParser(description='Protontypes - Automated Funding')
parser.add_argument("--folder", required=True, type=str,
                    help="Git folder to scan")

args = parser.parse_args()
git_folder = args.folder

# Load parameters from environment variables

libraries_api_key = os.environ['LIBRARIES_IO_TOKEN']
github_token = os.environ['GITHUB_TOKEN']
coinbase_token = os.environ['COINBASE_TOKEN']
coinbase_secret = os.environ['COINBASE_SECRET']

librariesIO = LibrariesIOConnector(libraries_api_key)
gitConnector = GithubConnector(github_token)
coinConnector = CoinbaseConnector(coinbase_token,coinbase_secret)

# Scan for Project Contributors
target_remote=gitremotes.ScanRemotes(git_folder,'origin')
project_id = gitConnector.GetProjectID(target_remote) 
project_email_list = gitConnector.getContributorInfo(project_id)
n_funding_emails=1
amount='0.00001'
funding_emails=random.choices(project_email_list, weights = [ 1 for i in range(len(project_email_list))], k=n_funding_emails)
for email in funding_emails:
    receipt = coinConnector.payout(email)
    print(receipt)
    f = open("receipt.txt", "a")
    f.write(str(receipt))
    f.close()

# Scan for Dependencies
run_path = os.path.dirname(os.path.realpath(__file__))
status = subprocess.call('ruby '+run_path+'/scripts/scan.rb --project='+git_folder, shell=True)


if status == 0:
    with open('/home/proton/.protontypes/dependencies.json') as f:
        dependencies_json = json.load(f)
else:
     print("Can not find dependencies.json file")
     exit()


dependencies_json = protonutils.getUniqueDependencies(dependencies_json)
dependency_list = []
for platform_name in dependencies_json.keys():

    if not dependencies_json[platform_name]:
        continue
    for deps in dependencies_json[platform_name]:
        name = deps["name"]
        dependency = {"platform": platform_name, "name": name}
        ownerandproject = librariesIO.getOwnerandProject(platform_name, name)
        if not ownerandproject:
            continue
        depData = librariesIO.getDependencyData(
            ownerandproject["owner"], ownerandproject["project_name"])
        if not depData:
            continue
        dependency["dependencies"] = depData["dependencies"]
        dependency["github_id"] = depData["github_id"]

        email_list = gitConnector.getContributorInfo(dependency["github_id"])
        dependency["email_list"] = email_list
        print("Emails for " + name)
        print("Number vaild emails entries:")
        print(len(email_list))
        dependency_list.append(dependency)
