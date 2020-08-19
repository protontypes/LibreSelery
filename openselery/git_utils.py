import git
import os
import re


def find_involved_commits(repo_path, endIdentifier):
    repo = git.Repo(repo_path)
    endCommit = endIdentifier.git_find(repo)

    if endCommit:
        return find_commits_between_commits(repo_path, repo.commit("HEAD"), endIdentifier.git_find(repo))

    return []

def find_commits_between_commits(repo_path, start, end):
    repo = git.Repo(repo_path)
    commits = repo.git.rev_list("--ancestry-path", end.hexsha + ".." + start.hexsha).split(os.linesep)

    return list(map(lambda c: repo.commit(c), commits))

def grabLocalProject(repo_path, remoteName="origin"):
    repo = git.Repo(repo_path)
    for remote in repo.remotes:
        if remote.name == remoteName:
            return remote.url
        else:
            raise Exception("No Remote URL found")


def ScanCommits(git_folder, branch="master"):
    repo = git.Repo(git_folder)
    commit_msgs = []
    commits = list(repo.iter_commits("master"))
    for c in commits:
        commit_msg = {"name": str(c.author), "email": c.author.email, "msg": c.message}
        commit_msgs.append(commit_msg)
    return commit_msgs


def get_head_sha(git_folder):
    repo = git.Repo(git_folder, search_parent_directories=True)
    return repo.head.object.hexsha


def get_lastest_tag(git_folder):
    repo = git.Repo(git_folder, search_parent_directories=True)
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    return tags[-1]
