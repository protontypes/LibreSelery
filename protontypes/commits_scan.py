from git import Repo, Commit

def ScanCommits(git_folder,branch='master'):
    repo = Repo(git_folder)
    commit_msgs = []
    commits = list(repo.iter_commits('master'))
    for c in commits:
        commit_msg = {'name': str(c.author), 'email': c.author.email, 'msg': c.message} 
        commit_msgs.append(commit_msg)
    return commit_msgs

if __name__ == "__main__":
    pass
