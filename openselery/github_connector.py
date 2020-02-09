import time
import re
from github import Github, StatsContributor

from openselery import selery_utils
from pprint import pprint, PrettyPrinter

class Contributor(object):
    def __init__(self, fromProject, c):
        self.fromProject = fromProject
        self.stats = c

    def __repr__(self):
        result = "Contributor("
        result += "fromProject: "
        result += str(self.fromProject)
        result += ", "
        result += "stats: "
        result += str(self.stats)
        result += ")"
        return result

class GithubConnector(selery_utils.Connector):
    def __init__(self, token):
        super(GithubConnector, self).__init__()
        self.github = Github(login_or_token=token)

    def grabRemoteProject(self, projectId):
        project = self.github.get_repo(int(projectId))
        return project

    def parseRemoteProjectId(self, url):

        # These urls need to be parsable:
        # https://github.com/protontypes/openselery
        # https://github.com/protontypes/openselery.git
        # git@github.com:protontypes/protontypes.git

        matchObj = re.match(
            "^(?:git@|https://)[^/:]+[/:]([^/]+)/([^/]+?)(?:\.git)?$", url)
        if not matchObj:
            raise ValueError("url cannot be parsed. (url: %s)" % (url))

        (owner, project_name) = matchObj.groups()
        repo = self.github.get_repo(owner + '/' + project_name)
        return repo.id

    def grabRemoteProjectByUrl(self, projectUrl):
        projectId = self.parseRemoteProjectId(projectUrl)
        localproject = self.grabRemoteProject(projectId)
        return localproject

    def grabRemoteProjectContributors(self, project):
        cachedContributors = []
        contributors = project.get_stats_contributors()  # .get_contributors()
        # cash collect all contributors by iterating over them
        for c in contributors:
            cachedContributors.append(Contributor(project.html_url, c))

        # cash collect all contributors by iterating over them
        # for contributor in contributors:
        #    requests_remaining = self.github.rate_limiting
        #    if requests_remaining[0] < 100:
        #        wait_time = self.github.rate_limiting_resettime - int(time.time())
        #        print("No Github requests remaining")
        #        selery_utils.countdown(wait_time)
        #
        #    # contr_id = contributor.id
        #    # location = contributor.location
        return cachedContributors

    # def ScanCommits(git_folder,branch='master'):
    #    repo = Repo(git_folder)
    #    commit_msgs = []
    #    commits = list(repo.iter_commits('master'))
    #    for c in commits:
    #        commit_msg = {'name': str(c.author), 'email': c.author.email, 'msg': c.message}
    #        commit_msgs.append(commit_msg)
    #    return commit_msgs
