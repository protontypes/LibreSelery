#!/usr/bin/python3

from git import Repo, Commit
import argparse,os

parser =  argparse.ArgumentParser(description='Protontypes - Random Donation')
parser.add_argument("--project", required=True, type=str, help="Project root folder to scan")

args = parser.parse_args()
root_folder = args.project

#repo = Repo.clone_from('git@github.com:smappi/smappi.git', '/tmp/xxx')
repo = Repo(root_folder)
commits = list(repo.iter_commits('master'))
for c in commits:
    commit = {'name': str(c.author), 'email': c.author.email, 'msg': c.message} 
    print(commit)
