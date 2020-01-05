#!/usr/bin/python3
import argparse
import sqlite3
import subprocess
import os
import random
import time
import json
from datetime import datetime
from git import Repo
from github import Github
from shutil import rmtree

parser = argparse.ArgumentParser()
parser.add_argument("--clonefolder", required=True, type=str,
                    help="Folder to clone into")

args = parser.parse_args()
clone_folder = args.clonefolder

run_path = os.path.dirname(os.path.realpath(__file__))

# Load parameters from environment variables

github_token = os.environ['GITHUB_TOKEN']

try:
   db_conn = sqlite3.connect("/home/celery/db/gitclones.sqlite3")
except:
   db_conn = sqlite3.connect("gitclones.sqlite3")
db_cursor = db_conn.cursor()

sqlite_create_table = "CREATE TABLE IF NOT EXISTS dependencies(url TEXT, dependencies TEXT, request_date DATETIME)"
db_cursor.execute(sqlite_create_table)
db_conn.commit()

def saveJsonIntoDB(url, dependencies):
   # check if url already exist in DB
   sqlite_select_query = """SELECT url from dependencies WHERE url = ?"""
   db_cursor.execute(sqlite_select_query, (url,))
   repo = db_cursor.fetchall()
   if(repo):
      print(url + "already exists!")
      return
   # save dependencies into db
   time_ = datetime.now().strftime("%B %d, %Y %I:%M%p")
   data_tuple = (url, dependencies, time_)
   sqlite_insert_with_param = """INSERT INTO 'dependencies'
                          ('url', 'dependencies', 'request_date') 
                          VALUES (?, ?, ?);"""
   db_cursor.execute(sqlite_insert_with_param, data_tuple)
   db_conn.commit()


g = Github(github_token)
# https://help.github.com/en/github/searching-for-information-on-github/understanding-the-search-syntax

min_stars=100
upper_bound_stars=2000
max_stars=random.randint(min_stars, upper_bound_stars)
repositories = g.search_repositories(query='stars:'+str(min_stars)+'..'+str(max_stars))

for repo in repositories:
   if repo.size>100000:
       print("Skipped "+repo.clone_url)
       continue
   print("Clone repo "+repo.clone_url)
   Repo.clone_from(repo.clone_url,clone_folder+"/"+repo.name)
   print("scan with bibliothecary..")
   status = subprocess.call('ruby '+run_path+'/../scripts/scan.rb --project='+clone_folder, shell=True)
   dependencies_json = None
   if status == 0:
      with open ('dependencies.json') as f:
         dependencies_json = f.read().replace('\n', '')
   #print(dependencies_json)
   saveJsonIntoDB(repo.clone_url, dependencies_json)

   for dirct in os.listdir(os.path.join(clone_folder)):
      rmtree(os.path.join(clone_folder,dirct))

   #print(repo.clone_url)
   #print(repo.get_languages)
   time.sleep(2)
      
