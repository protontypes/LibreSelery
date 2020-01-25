import dns.resolver


# dep_list: list of dependencies, each dependency has a contributors list
# returns: list of dependencies, each dependency has a contributors list with accociated weights
def getUniqueDependencies(dependencies_json):
    uniqueList = dict()
    for platform in dependencies_json:
        if not platform["dependencies"]:
            continue
        platform_name = platform["platform"]
        if platform_name not in uniqueList.keys():
            uniqueList[platform_name] = []
        for dep in platform["dependencies"]:
            if dep not in uniqueList[platform_name]:
                uniqueList[platform_name].append(dep)
    return uniqueList


import time


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
        print("...")


def checkMail(mail):
    valid = True
    # regex = r'\b[\w.-]+?@\w+?\.\w+?\b'
    # if re.fullmatch(regex, mail) is not None:
    try:
        dns.resolver.query(mail.split('@')[1], "MX")[0].exchange
    except Exception as e:
        valid = False
    return valid


def validateContributor(contributor, minimum_contributions=0):
    if not contributor:
        return False

    ### ignore contributos with less than num_contrib contributions
    if contributor.total < minimum_contributions:
        return False
    ### ignore contributos with no or bad email
    email = contributor.author.email
    if email is None:
        return False
    elif not checkMail(contributor.author.email):
        return False

    return True


def validateContributors(contributors, minimum_contributions):
    valid = []
    for c in contributors:
        if validateContributor(c, minimum_contributions):
            valid.append(c)
    return valid
