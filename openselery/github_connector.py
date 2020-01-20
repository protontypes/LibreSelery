from github import Github
from .email_checker import EmailChecker
from .seleryutils import countdown
from urllib.parse import urlparse
import time


class GithubConnector:
    def __init__(self, github_token):
        self.github = Github(github_token)

    def getContributorInfo(self, id, num_contrib=1):
        try:
            repo = self.github.get_repo(int(id))
        except:
            return []
        contributors = repo.get_stats_contributors()  # .get_contributors()
        emails_list = []
        for contributor in contributors:
            requests_remaining = self.github.rate_limiting
            if requests_remaining[0] < 100:
                wait_time = self.github.rate_limiting_resettime - \
                    int(time.time())
                print("No Github requests remaining")
                countdown(wait_time)

            #contr_id = contributor.id
            #location = contributor.location

            # ignore contributos with less than num_contrib contributions
            if contributor.total < num_contrib:
                continue
            try:
                email = contributor.author.email
            except Exception as e:
                print(e)
                email = ""

            if EmailChecker.checkMail(email):
                emails_list.append(
                    {"email": email, "contributions": contributor.total})
            else:
                if(email):
                    print("wrong email " + email)

        return emails_list

    def getGithubID(self, repo_url):
        parser = urlparse(repo_url)
        owner = parser.path.split('/')[1]
        project_name = parser.path.split('/')[2]
        try:
            project_name = project_name.split('.')[0]
        except:
            pass
        repo = self.github.get_repo(owner+'/'+project_name)
        return repo.id


if __name__ == "__main__":
    pass
