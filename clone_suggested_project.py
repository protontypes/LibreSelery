#!/usr/bin/python3

from git import Repo, Commit
import argparse,os
from gitsuggest import GitSuggest

parser =  argparse.ArgumentParser(description='')
parser.add_argument("--user", required=True, type=str, help="User to get Suggestions")

args = parser.parse_args()
github_user = args.user

# To use with username password combination
# gs = GitSuggest(username=<username>, password=<password>)
#
# # To use with access_token
# gs = GitSuggest(token=access_token)
#
# To use without authenticating
gs = GitSuggest(username=github_user)
#
# # To use with deep dive flag
# gs = GitSuggest(username=<username>, password=<password>, token=None, deep_dive=True)
# gs = GitSuggest(token=access_token, deep_dive=True)
# gs = GitSuggest(username=<username>, deep_dive=True)
#
# # To get an iterator over suggested repositories.
print(gs.get_suggested_repositories())

