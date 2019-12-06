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


class GithubConnector:
    def __init__(self, github_token):
        self.github = Github(github_token)

    def getContributorEmails(self, id):      
        print(id)  
        try:
            repo = self.github.get_repo(int(id))
        except:
            return []
        contributors = repo.get_contributors()
        emails_list = []
        for contributor in contributors:
            if contributor.email:
                emails_list.append(contributor.email)

        return emails_list


class LibrariesIOConecter:
    def __init__(self, key):
        self.apiKey = {'api_key':key}
        self.base_url = 'https://libraries.io/'

    def getOwner(self, platform, name):
        url_path = posixpath.join('api',platform,name)
        url = urllib.parse.urljoin(self.base_url,url_path)
        r = requests.get(url,params=self.apiKey)
        if r.status_code is not 200:
            print("Request not possible")
            print(r.status_code)
            print(r.text)
            return None
        else:
            repository_url=r.json().get('repository_url')
            owner = repository_url.split('/')[-2]
            return owner
    
    def getDependencyData(self, owner, name):
        url_path = posixpath.join('api','github',owner,name,'dependencies')
        url = urllib.parse.urljoin(self.base_url,url_path)
        r = requests.get(url,params=self.apiKey)
        if r.status_code is not 200:
            print("Request not possible")
            print(r.status_code)
            print(r.text)
            return None
        else:
            return {"dependencies": r.json().get('dependencies'), "github_id": r.json().get('github_id')}

librariesIO = LibrariesIOConecter(libraries_api_key)
gitConnector = GithubConnector(github_token)

status = subprocess.call('ruby scan.rb --project='+root_folder, shell=True)
dependencies_json = None
if status==0:
    with open('dependencies.json') as f:
        dependencies_json = json.load(f)
dependency_list = []
for platform in dependencies_json:
    platform_name = platform["platform"]
    for deps in platform["dependencies"]:
        name = deps["name"]        
        dependency = {"platform": platform_name, "name":name}
        dependency["owner"] = librariesIO.getOwner(platform_name, name)
        depData = librariesIO.getDependencyData(dependency["owner"], name)
        dependency["dependencies"] = depData["dependencies"]
        dependency["github_id"] = depData["github_id"]
        
        email_list = gitConnector.getContributorEmails(dependency["github_id"])
        dependency["email_list"] = email_list
        print("Emails for " + name)
        print(email_list)
        dependency_list.append(dependency)
    
print(dependency_list)



