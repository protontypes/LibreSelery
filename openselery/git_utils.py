
import git
import re

def find_release_contributor(repo_path,number_of_):
    repo = git.Repo(repo_path)
    tags = repo.tags

    k = 0
    commits = {}
    last_release_contributor = []
    for check_tag in reversed(tags):
        print(check_tag)
        if re.match("^[v](\d+\.)?(\d+\.)?(\*|\d+)$", str(check_tag)) is not None:
            last_release_tag = check_tag
            break
        k = k + 1

    last_release_commits_sha = repo.git.log(
        "--oneline", "--format=format:%H", str(last_release_tag)+"..master").splitlines()

    for git_commit in repo.iter_commits():
        commits[git_commit.hexsha] = git_commit

    for sha in last_release_commits_sha:
        commit = commits[sha]
        last_release_contributor.append(commit.author.email)
    print(last_release_contributor)

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
