#!/usr/bin/python3
import subprocess
import argparse
import os
import json
import re
from protontypes.github_connector import GithubConnector
from protontypes.librariesio_connector import LibrariesIOConnector

parser = argparse.ArgumentParser(description='Protontypes - Random Donation')
parser.add_argument("--project", required=True, type=str,
                    help="Project root folder to scan")

args = parser.parse_args()
root_folder = args.project

# Load parameters from environment variables

libraries_api_key = os.environ['LIBRARIES_IO_TOKEN']
github_token = os.environ['GITHUB_TOKEN']


librariesIO = LibrariesIOConnector(libraries_api_key)
gitConnector = GithubConnector(github_token)

status = subprocess.call('ruby scan.rb --project='+root_folder, shell=True)
dependencies_json = None
if status == 0:
    with open('dependencies.json') as f:
        dependencies_json = json.load(f)


def getUniqueDependencies(dependencies_json):
    uniqueList = dict()
    for platform in dependencies_json:
        if not platform["dependencies"]:
            continue
        platform_name = platform["platform"]
        if platform_name not in uniqueList.keys():
            uniqueList[platform_name] = []
        for dep in platform["dependencies"]:
            if dep not in uniqueList[platform_name]:
                uniqueList[platform_name].append(dep)
    return uniqueList


dependencies_json = getUniqueDependencies(dependencies_json)


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

        email_list = gitConnector.getContributorEmails(dependency["github_id"])
        dependency["email_list"] = email_list
        print("Emails for " + name)
        print(email_list)
        dependency_list.append(dependency)

print(dependency_list)
