#!/usr/bin/python3
import argparse
import os
import random
from git import Repo
from github import Github
parser = argparse.ArgumentParser()
parser.add_argument("--clonefolder", required=True, type=str,
                    help="Folder to clone into")

args = parser.parse_args()
clone_folder = args.clonefolder

# Load parameters from environment variables
#
github_token = os.environ['GITHUB_TOKEN']
#
g = Github(github_token)
# # https://help.github.com/en/github/searching-for-information-on-github/understanding-the-search-syntax
#
min_stars = 100
upper_bound_stars = 2000
max_stars = random.randint(min_stars, upper_bound_stars)
repositories = g.search_repositories(
    query='stars:'+str(min_stars)+'..'+str(max_stars))
for repo in repositories:
    Repo.clone_from(repo.clone_url, clone_folder+"/"+repo.name)
    print(repo.clone_url)
    print(repo.get_languages)
