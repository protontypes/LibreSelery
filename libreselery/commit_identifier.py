import re


def CommitIdentifierFromString(str):
    if str.startswith("tag_regex:"):
        regex = ":".join(str.split(":")[1:-1])
        return TagRegexCommitIdentifier(regex)
    if str.startswith("commit:"):
        commit = ":".join(str.split(":")[1:-1])
        return ExactCommitIdentifier(commit)
    if str == "none":
        return CommitIdentifier()

    return None


class CommitIdentifier(object):
    def git_find(self, repo):
        return None


class ExactCommitIdentifier(CommitIdentifier):
    def __init__(self, identifier):
        self.identifier = identifier

    def git_find(self, repo):
        return repo.commit(self.identifier)


class TagRegexCommitIdentifier(CommitIdentifier):
    def __init__(self, regex):
        self.regex = regex

    def git_find(self, repo):
        for tag in reversed(repo.tags):
            tag_str = str(tag)
            if re.match(self.regex, tag_str):
                return repo.commit(tag_str)

        return None
