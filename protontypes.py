#!/usr/bin/python

import requests,urllib,posixpath,subprocess,argparse
from github import Github
import json

parser =  argparse.ArgumentParser(description='Protontypes - Random Donation')
parser.add_argument("--project", required=True, type=str, help="Project root folder to scan")

args = parser.parse_args()
root_folder = args.project
print(root_folder)

## Load parameters
with open('tokens.json') as f:
    tokens_data = json.load(f)
libraries_api_key = tokens_data["libraries_io_api_key"]
github_token = tokens_data["github_token"]

status = subprocess.call('ruby scan.rb', shell=True)
if status==0:
    with open('dependencies.json') as f:
        dependencies_json = json.load(f)
dependency_list = []
for platform in dependencies_json:
    platform_name = platform["platform"]
    for deps in platform["dependencies"]:
        name = deps["name"]
        dependency_list.append({"platform": platform_name, "name":name})

base_url = 'https://libraries.io/'
owner='tensorflow'
name='tensorflow'
version='latest'
libraries_io_api_key = {'api_key':libraries_api_key}
keyword = 'dependencies'
ok_code = 200
url_path = posixpath.join('api','github',owner,name,keyword)
url = urllib.parse.urljoin(base_url,url_path)
r = requests.get(url,params=libraries_io_api_key)
if r.status_code is not ok_code:
    print("Request not possible")
    print(r.status_code)
    print(r.text)
    exit()
print(r.json().get('dependencies'))
repository_url=r.json().get('repository_url')
print(r.json().keys())

g = Github(github_token)
github_id = int(r.json().get("github_id"))

repo = g.get_repo(github_id)

cotributors = repo.get_contributors()

for contributor in cotributors:
    print(contributor.email)

