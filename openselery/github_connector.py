import time
from urllib.parse import urlparse

from github import Github
from git import Repo, Commit

from openselery import selery_utils


class GithubConnector:
    def __init__(self, token):
        self.github = Github(login_or_token=token)
        try:
            pId = self.github.get_user().id
        except Exception as e:
            raise ConnectionError("Could not connect to Github")

    def grabRemoteProject(self, projectId):
        project = self.github.get_repo(int(projectId))
        return project

    def parseRemoteProjectId(self, url):
        repoId = None
        parser = urlparse(url)
        owner = parser.path.split('/')[1]
        project_name = parser.path.split('/')[2]
        try:
            project_name = project_name.split('.')[0]
            repo = self.github.get_repo(owner + '/' + project_name)
            repoId = repo.id
        except Exception as e:
            pass
        return repoId

    def grabLocalProject(self, directory, remoteName='origin'):
        project = None
        projectUrl = None
        repo = Repo(directory)
        for remote in repo.remotes:
            if remote.name == remoteName:
                projectUrl = remote.url
                break
        if projectUrl:
            projectId = self.parseRemoteProjectId(projectUrl)
            if projectId:
                project = self.grabRemoteProject(projectId)
        return project

    def grabRemoteProjectContributors(self, project):
        contributors = project.get_stats_contributors()  # .get_contributors()
        ### cash collect all contributors by iterating over them
        for contributor in contributors:
            requests_remaining = self.github.rate_limiting
            if requests_remaining[0] < 100:
                wait_time = self.github.rate_limiting_resettime - int(time.time())
                print("No Github requests remaining")
                selery_utils.countdown(wait_time)

            # contr_id = contributor.id
            # location = contributor.location
        return contributors
