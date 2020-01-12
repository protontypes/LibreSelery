from git import Repo, Commit

def scanSubmodules(git_folder,branch='master'):
    repo = Repo(git_folder)
    module_urls=[]
    for module in repo.iter_submodules():
        modules_urls.append(module.url)
    return module

def scanRemotes(git_folder,remote_name='origin'):
    repo = Repo(git_folder)
    target_url=''
    for remote in repo.remotes:
        if remote.name == remote_name:
            target_url = remote.url
    return target_url

# ToDO git subtree missing

if __name__ == "__main__":
    pass
