#!/usr/bin/python

import requests,os,urllib,posixpath,sys,base64,re
from urlextract import URLExtract
from github import Github
import json

## Load parameters
with open('tokens.json') as f:
    tokens_data = json.load(f)
libraries_api_key = tokens_data["libraries_io_api_key"]
github_token = tokens_data["github_token"]


base_url = 'https://libraries.io/'
api='api'
owner='tensorflow'
name='tensorflow'
version='latest'
libraries_io_api_key = {'api_key':libraries_api_key}
keyword = 'dependencies'
ok_code = 200
url_path = posixpath.join(api,'github',owner,name,keyword)
url = urllib.parse.urljoin(base_url,url_path)
r = requests.get(url,params=libraries_io_api_key)
if r.status_code is not ok_code:
    print("Request not possible")
    print(r.status_code)
    print(r.text)
    sys.exit()
print(r.json().get('dependencies'))
repository_url=r.json().get('repository_url')
print(r.json().keys())

#for key in r.json().keys():
#    print()
#    print(key)
#    print(r.json().get(key))



# Not needed
g = Github()
github_id = int(r.json().get("github_id"))
print(github_id)
print(type(github_id))

repo = g.get_repo(github_id)

cotributors = repo.get_contributors()

for contributor in cotributors:
    print(contributor.email)

