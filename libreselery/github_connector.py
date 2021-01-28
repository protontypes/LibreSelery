import time
import re
from github import Github, StatsContributor

from libreselery import selery_utils


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

    def parseRemoteToOwnerProjectName(self, url):
        # These urls need to be parsable:
        # https://github.com/protontypes/libreselery
        # https://github.com/protontypes/libreselery.git
        # git@github.com:protontypes/protontypes.git

        matchObj = re.match(
            r"^(?:git@|https://)[^/:]+[/:]([^/]+)/([^/]+?)(?:\.git)?$", url
        )
        if not matchObj:
            raise ValueError("url cannot be parsed. (url: %s)" % (url))

        (owner, project_name) = matchObj.groups()
        return owner + "/" + project_name

    def parseRemoteProjectId(self, url):
        repo = self.github.get_repo(self.parseRemoteToOwnerProjectName(url))
        return repo.id

    def grabRemoteProjectByUrl(self, projectUrl):
        projectId = self.parseRemoteProjectId(projectUrl)
        localproject = self.grabRemoteProject(projectId)
        return localproject

    def grabRemoteProjectContributors(self, project):
        cachedContributors = []
        attempts = 0
        max_attempts = 5
        while attempts <= max_attempts:
            try:
                contributors = project.get_stats_contributors()  # .get_contributors()
                break
            except:
                print("Retry Connections to Github")
                attempts += 1
                time.sleep(5.0)
        if attempts >= max_attempts:
            raise KeyError("Not able to connect to Github with current credentials")

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

    def grabUserNameByEmail(self, email):
        user = self.github.search_users(str(email) + " in:email")
        return email

    # def ScanCommits(git_folder,branch='master'):
    #    repo = Repo(git_folder)
    #    commit_msgs = []
    #    commits = list(repo.iter_commits('master'))
    #    for c in commits:
    #        commit_msg = {'name': str(c.author), 'email': c.author.email, 'msg': c.message}
    #        commit_msgs.append(commit_msg)
    #    return commit_msgs
