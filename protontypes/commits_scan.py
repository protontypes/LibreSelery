from git import Repo, Commit

class CommitsScanner
    def __init__(self):
        pass

    @staticmethod
    def ScanLocal(git_folder,branch='master'):
        repo = Repo(git_folder)
        commit_msgs = []
        commits = list(repo.iter_commits('master'))
        for c in commits:
            commit_msg = {'name': str(c.author), 'email': c.author.email, 'msg': c.message} 
            commits_msgs.append(commit_msg)
        return commits_msgs

if __name__ = "___main__":
    pass
