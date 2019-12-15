#!/usr/bin/python3

from git import Repo
import argparse,os

parser =  argparse.ArgumentParser(description='Protontypes - Random Donation')
parser.add_argument("--project", required=True, type=str, help="Project root folder to scan")

args = parser.parse_args()
root_folder = args.project

repo = Repo(root_folder)
assert not repo.bare

fifty_first_commits = list(repo.iter_commits('master', max_count=30))
assert len(fifty_first_commits) == 30
# this will return commits 21-30 from the commit list as traversed backwards master
ten_commits_past_twenty = list(repo.iter_commits('master', max_count=10, skip=20))
assert len(ten_commits_past_twenty) == 10
assert fifty_first_commits[20:30] == ten_commits_past_twenty
