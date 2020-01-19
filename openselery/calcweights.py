# dep_list: list of dependencies, each dependency has a contributors list
# returns: list of dependencies, each dependency has a contributors list with accociated weights
#
def getEmailsAndWeights(dep_list):
    # print("dep_list:\n"+dep_list)

    # [ {dep['project_id']: {'contributors': [{'email': email, 'weight': 1} for email in dep['email_list']]}}  for dep in dep_list]

    contributor_emails = []
    #TODO:
    # get more information about each contributor
    # number commits
    # time spent on project (calculated from commits)
    # issues closed
    # successful pull requests
    #
    for dep in dep_list:
        contributor_emails.append(dep["email_list"])

    weights = [ 1 for i in range(len(contributor_emails[0]))]
    return contributor_emails, weights
