import requests
import urllib
import posixpath
from urllib.parse import urlparse
from datetime import datetime
import sqlite3
import pickle


class LibrariesIOConnector:
    def __init__(self, key):
        self.apiKey = {'api_key': key}
        self.base_url = 'https://libraries.io/'
        try:
            self.db_conn = sqlite3.connect("/home/proton/db.sqlite3")
        except Exception as e:
            print(e)
            self.db_conn = sqlite3.connect("db.sqlite3")
        self.db_cursor = self.db_conn.cursor()
        # create table
        sqlite_create_table = "CREATE TABLE IF NOT EXISTS librariesio_responses(url TEXT, response BLOB, request_date DATETIME)"
        self.sqlite_insert_with_param = """INSERT INTO 'librariesio_responses'
                          ('url', 'response', 'request_date') 
                          VALUES (?, ?, ?);"""
        self.db_cursor.execute(sqlite_create_table)
        self.db_conn.commit()

    def getOwnerandProject(self, platform, name):
        url_path = posixpath.join('api', platform, name)
        url = urllib.parse.urljoin(self.base_url, url_path)
        r = self.makeRequest(url)
        if r.status_code is not 200 or r.json().get('repository_url') is None:
            print(platform+" "+name)
            print("Request not possible")
            print(r.status_code)
            return None
        else:
            try:
                repository_url = urlparse(r.json().get('repository_url'))
                owner = repository_url.path.split('/')[1]
                project_name = repository_url.path.split('/')[2]
                return {"owner": owner, "project_name": project_name}
            except:
                print("Repository URL is not valid")
                print(owner+":"+projectname)
                return None

    def getDependencyData(self, owner, name):
        name = name.replace(".git", "")
        url_path = posixpath.join('api', 'github', owner, name, 'dependencies')
        url = urllib.parse.urljoin(self.base_url, url_path)
        r = self.makeRequest(url)
        if r.status_code is not 200:
            print(owner+" "+name)
            print("Request not possible")
            print(r.status_code)
            return None
        else:
            return {"dependencies": r.json().get('dependencies'), "github_id": r.json().get('github_id')}

    def makeRequest(self, url):
        # 1. Check if the response is in the database
        sqlite_select_query = """SELECT response from librariesio_responses WHERE url = ?"""
        self.db_cursor.execute(sqlite_select_query, (url,))
        responses = self.db_cursor.fetchall()
        if(responses):
            print("Load response from db")
            r = pickle.loads(responses[0][0])
            return r
        r = requests.get(url, params=self.apiKey)
        if(r.ok):
            r_pickle = pickle.dumps(r)
            time = datetime.now().strftime("%B %d, %Y %I:%M%p")
            data_tuple = (url, r_pickle, time)
            self.db_cursor.execute(
                self.sqlite_insert_with_param, data_tuple)
            self.db_conn.commit()
            print("save response into db")
        return r


if __name__ == "__main__":
    pass
