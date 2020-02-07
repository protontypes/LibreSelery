
import git
import re


def find_release_contributor(repo_path, releases):
    repo = git.Repo(repo_path)
    tags = repo.tags

    # crosscheck releases rev_list and tags
    sha = repo.git.rev_list('--tags', '--max-count='+str(releases))
    describe_last_tag = repo.git.describe('--tags', sha.splitlines()[-1])

    k = 0
    commits = {}
    last_release_contributor_email = []
    for check_tag in reversed(tags):
        print(check_tag)
        if re.match("^[v](\d+\.)?(\d+\.)?(\*|\d+)$", str(check_tag)) is not None:
            if describe_last_tag == check_tag:
                break

        k = k + 1

    last_release_commits_sha = repo.git.log(
        "--oneline", "--format=format:%H", str(check_tag)+"..master").splitlines()

    for git_commit in repo.iter_commits():
        commits[git_commit.hexsha] = git_commit

    for sha in last_release_commits_sha:
        commit = commits[sha]
        last_release_contributor_email.append(commit.author.email)
    return last_release_contributor_email


def grabLocalProject(repo_path, remoteName='origin'):
    repo = git.Repo(repo_path)
    project = None
    projectUrl = None
    for remote in repo.remotes:
        if remote.name == remoteName:
            return remote.url
        else:
            print(process.stderr)
            raise Exception("No Remote URL found")


def ScanCommits(git_folder, branch='master'):
    repo = Repo(git_folder)
    commit_msgs = []
    commits = list(repo.iter_commits('master'))
    for c in commits:
        commit_msg = {'name': str(
            c.author), 'email': c.author.email, 'msg': c.message}
        commit_msgs.append(commit_msg)
    return commit_msgs
