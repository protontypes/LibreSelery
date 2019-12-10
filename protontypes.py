#!/usr/bin/python

import requests,urllib,posixpath,subprocess,argparse
from urllib.parse import urlparse
from github import Github
import json
import re
import dns.resolver

parser =  argparse.ArgumentParser(description='Protontypes - Random Donation')
parser.add_argument("--project", required=True, type=str, help="Project root folder to scan")

args = parser.parse_args()
root_folder = args.project

## Load parameters
with open('tokens.json') as f:
    tokens_data = json.load(f)
libraries_api_key = tokens_data["libraries_io_api_key"]
github_token = tokens_data["github_token"]

class EmailChecker:
    def __init__(self):
        pass
    @staticmethod
    def checkMail( mail):
        #regex = r'\b[\w.-]+?@\w+?\.\w+?\b'
        #if re.fullmatch(regex, mail) is not None:
        try:
            dns.resolver.query(mail.split('@')[1],"MX")[0].exchange
            return True
        except:
            return False
        return False

class GithubConnector:
    def __init__(self, github_token):
        self.github = Github(github_token)


    def getContributorEmails(self, id):        
        print(id)
        print(self.github.get_rate_limit())

        try:
            repo = self.github.get_repo(int(id))
        except:
            return []
        contributors = repo.get_contributors()
        emails_list = []
        for contributor in contributors:
            if contributor.email:
                if EmailChecker.checkMail(contributor.email):
                    emails_list.append(contributor.email)
                else:
                    print("wrong email " + contributor.email)
        return emails_list


class LibrariesIOConnecter:
    def __init__(self, key):
        self.apiKey = {'api_key':key}
        self.base_url = 'https://libraries.io/'

    def getOwnerandProject(self, platform, name):
        url_path = posixpath.join('api',platform,name)
        url = urllib.parse.urljoin(self.base_url,url_path)
        r = requests.get(url,params=self.apiKey)
        if r.status_code is not 200 or r.json().get('repository_url') is None:
            print(platform+" "+name)
            print("Request not possible")
            print(r.status_code)
            return None
        else:
            print(r.json().get('repository_url'))
            repository_url=urlparse(r.json().get('repository_url'))
            owner = repository_url.path.split('/')[1]
            project_name = repository_url.path.split('/')[2]
            return {"owner": owner, "project_name": project_name }

    def getDependencyData(self, owner, name):
        name = name.replace(".git","")
        url_path = posixpath.join('api','github',owner,name,'dependencies')
        url = urllib.parse.urljoin(self.base_url,url_path)
        r = requests.get(url,params=self.apiKey)
        if r.status_code is not 200:
            print(owner+" "+name)
            print("Request not possible")
            print(r.status_code)
            return None
        else:
            return {"dependencies": r.json().get('dependencies'), "github_id": r.json().get('github_id')}

librariesIO = LibrariesIOConnecter(libraries_api_key)
gitConnector = GithubConnector(github_token)

status = subprocess.call('ruby scan.rb --project='+root_folder, shell=True)
dependencies_json = None
if status==0:
    with open('dependencies.json') as f:
        dependencies_json = json.load(f)


def getUniqueDependencies(dependencies_json):
    uniqueList = dict()
    for platform in dependencies_json:
        if not platform["dependencies"]:
            continue
        platform_name = platform["platform"]
        if platform_name not in uniqueList.keys():
                uniqueList[platform_name]=[]
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
        dependency = {"platform": platform_name, "name":name}
        ownerandproject = librariesIO.getOwnerandProject(platform_name, name)
        if not ownerandproject:
            continue
        depData = librariesIO.getDependencyData(ownerandproject["owner"],ownerandproject["project_name"])
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
