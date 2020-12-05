import time
import dns.resolver


class Connector(object):
    def __init__(self):
        super(Connector, self).__init__()


# dep_list: list of dependencies, each dependency has a contributors list
# returns: list of dependencies, each dependency has a contributors list with accociated weights
def getUniqueDependencies(dependencies_json):
    unique = {}
    for entry in dependencies_json:
        if not entry["dependencies"]:
            continue
        platform = entry["platform"]
        if platform not in unique.keys():
            unique[platform] = []
        for dep in entry["dependencies"]:
            if dep not in unique[platform]:
                unique[platform].append(dep)
    return unique


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = "{:02d}:{:02d}".format(mins, secs)
        print(timeformat, end="\r")
        time.sleep(1)
        t -= 1
        print("...")


def checkMail(mail):
    valid = True
    # regex = r'\b[\w.-]+?@\w+?\.\w+?\b'
    # if re.fullmatch(regex, mail) is not None:
    try:
        dns.resolver.query(mail.split("@")[1], "MX")[0].exchange
    except Exception as e:
        valid = False
    return valid


# dep_list: list of dependencies, each dependency has a contributors list
# returns: list of dependencies, each dependency has a contributors list with accociated weights
def calculateContributorWeights(contributors, uniform_weight):
    # TODO: get more information about each contributor
    # * number commits
    # * time spent on project (calculated from commits)
    # * issues closed
    # * successful pull requests
    weights = [uniform_weight for i in range(len(contributors))]
    return weights


def weighted_split(contributors, weights, total_payout_amount):
    contributor_payout_split = []
    totalized_weights = sum(weights)
    for idx, contributor in enumerate(contributors):
        individual_split_amount = total_payout_amount * (
            weights[idx] / totalized_weights
        )
        contributor_payout_split.append(individual_split_amount)
    return contributor_payout_split
