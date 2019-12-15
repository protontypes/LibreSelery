from github import Github
from .email_checker import EmailChecker


class GithubConnector:
    def __init__(self, github_token):
        self.github = Github(github_token)

    def getContributorEmails(self, id):
        print(id)
        print(self.github.get_rate_limit())

        try:
            repo = self.github.get_repo(int(id))
        except:
            return []
        contributors = repo.get_contributors()
        emails_list = []
        for contributor in contributors:
            if contributor.email:
                if EmailChecker.checkMail(contributor.email):
                    emails_list.append(contributor.email)
                else:
                    print("wrong email " + contributor.email)
        return emails_list


if __name__ == "__main__":
    pass
