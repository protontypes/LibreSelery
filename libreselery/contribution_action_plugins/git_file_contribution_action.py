#! /usr/bin/python3

from libreselery.contribution_distribution_engine_types import (
    ContributionAction,
    ContributionActionPlugin,
)

### Start User Imports
### specialzed plugin imports can be added here
##################################################################################
import subprocess
from datetime import datetime

### End User Imports
##################################################################################


class GitFileContributionAction(ContributionActionPlugin):
    """
    This class is a plugin containing the implementation of a single ContributorAction.
    It is responsible for gathering contributor information and evaluating scores
    for each contributor based on configurated metrics

    Plugin description:
    This plugin will evaluate the line-of-code contributions made from all
    contributors of local files (under git version control).
    """

    _alias_ = "git_file_contribution_action"
    GITBLAMESEPERATOR = "***\n"

    def __init__(self):
        super(GitFileContributionAction, self).__init__()

    def initialize_(self, action):
        """
        Overload of abstract method which is responsible for initializing this plugin

        Parameters:
        action (ContributionAction):
            action object which contains all necessary information of what
            a contributor has to doto be scored and recognized as such

        Returns:
        bool: True if successfully initialized
        """
        return True

    def gather_(self, cachedContributors=[]):
        """
        Overload of abstract method which is responsible for gathering
        contributor information and scoring contributors based on the action defined

        Parameters:
        [optional] cachedContributors (list):
            list of contributors from various external (remote) sources which had been chached earlier
            so that plugins don't need to do expensive lookups all the time

        Returns:
        tuple: (list of contributors, list of scores)
        """
        contributors = []
        scores = []
        ### execute git commands to identify line contributions for each contributor
        ### per file under git version control
        fileContributions = self.execGit()
        ### iterate through all cointributions and separate contributors from files
        uniqueFileContributions = {}
        for filename, fileContributorDict in fileContributions.items():
            self.log("%s" % filename)
            ### extract and log necessary contributor data for the file
            contributorData = self.processFileContributorDict(fileContributorDict)
            ### sum up all contributions from each user in our final
            ### dict (contributon = lines of code)
            for author, count in contributorData.items():
                if author in uniqueFileContributions:
                    uniqueFileContributions[author] += count
                else:
                    uniqueFileContributions[author] = count
        ### extract contributors and scores list from summed up file contribution data
        blob = [*uniqueFileContributions.items()]
        contributors, linesOfCode = ([c for c, s in blob], [s for c, s in blob])
        ### convert linesOfCode to score
        ### we need to use given metrics for that
        ### our action was initialized with a metric, we have to use that instead of
        ### doing something random here
        ###
        ### in this simple example, each line of code represents 0.25 score points
        ###   --  this is bad, but it works for now as a reference
        ###   --  this cannot be a magic number, has to be configurable later
        scores = [0.25 * loc for loc in linesOfCode]
        ### done, return our data so that it can be used inside the CDE to
        ### weight the contributions made
        self.log(contributors)
        return contributors, scores

    ### Start User Methods
    ### specialzed plugin methods can be added here
    ##################################################################################

    def execGit(self):
        cmd = [
            "git",
            "ls-files",
            "|",
            "while read f;",
            'do echo "%s$f";' % self.GITBLAMESEPERATOR,
            "git blame -CCC --line-porcelain $f;",
            "done",
        ]

        ps = subprocess.Popen(
            " ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = ps.communicate()

        fileContributions = {}
        if not stderr:
            encoded = stdout.decode("utf-8")
            ### split output for each file (we added "\n" manually to seperate each file output)
            fileblames = encoded.split(self.GITBLAMESEPERATOR)[
                1:
            ]  ### 0 entry is empty because reasons ... :D
            for blame in fileblames:
                ### seperate lines into array
                lines = blame.split("\n")
                filename = lines[0]
                lines = lines[1:]
                ### put lines through blameParser
                fileContributorDict = self.parseBlame(lines)
                ### filter out unwanted users, for example the one git blame adds
                ### in case there are uncommitted changes
                ###     "<not.committed.yet>", "Not Committed Yet"
                if "not.committed.yet" in fileContributorDict:
                    del fileContributorDict["not.committed.yet"]
                fileContributions[filename] = fileContributorDict
        return fileContributions

    def processFileContributorDict(self, fcDict):
        fileContributions = {}
        for author, data in fcDict.items():
            contributionCount = data["count"]
            self.log("  %s [%s]" % (author, contributionCount))
            for stamp, count in data["stamps"].items():
                datetimeStr = datetime.fromtimestamp(float(stamp)).strftime(
                    "%Y-%m-%d/%H:%M:%S"
                )
                self.log("    -- %s [%s]" % (datetimeStr, count))
            fileContributions[author] = contributionCount
        return fileContributions

    def parseBlame(self, lines):
        lineDescriptions = []
        lineDescription = {}
        currentCommitSha = None
        headerLength = None
        newEntry = True
        for line in lines:
            if newEntry:
                newEntry = False
                ### commit hash extraction
                key = "commit"
                val = line.split(" ")[0]
            else:
                splits = line.split(" ")
                key = splits[0]
                val = " ".join(splits[1:])

            ### the amount of lines per entry is not consistent inside git blame
            ### so parsing is nearly impossible
            ### the only proper criteria in this stupid pocelain implementation is when we have a codeline which allways starts with \t
            ### thanks git ... idiots -.-
            if line and line[0] == "\t":
                ### valuable lines done
                lineDescriptions.append(lineDescription)
                lineDescription = {}
                newEntry = True

            lineDescription[key] = val

        fileContributions = {}
        for d in lineDescriptions:
            author_mail = d["author-mail"][1:-1]  ### strip leading and ending "<>"
            author_user = d["author"]
            timestamp = d["committer-time"]
            # key = (author_mail, author_user)
            key = author_mail
            dd = fileContributions.get(key, None)
            if dd:
                c = dd["count"]
                stamps = dd["stamps"]
                c += 1
                if timestamp in stamps:
                    stamps[timestamp] += 1
                else:
                    stamps[timestamp] = 1
                ### rewrite the dict data
                fileContributions[key] = {"count": c, "stamps": stamps}
            else:
                fileContributions[key] = {"count": 1, "stamps": {timestamp: 1}}
        return fileContributions

    ### End User Methods
    ##################################################################################


def test():
    success = False
    print("This is a Test!")
    ### define our input configuration (action) which normally comes from .yml configuration
    d = {
        "contributions_to_code": {
            "debug": True,
            "type": "git_file_contribution_action",  ### type of action (also the name of the plugin _alias_ used!)
            "applies_to": [
                "*.md",
                "docs/",
            ],  ### simple filter, not really thought out yet
            "metrics": [  ### metrics applied to this action, what gets score and what doesnt
                {
                    "UNIFORM": {  ### metric identifier
                        "degradation_type": "linear",
                        "degradation_value": 1,
                    }
                }
            ],
        }
    }
    ### create an action object
    action = ContributionAction(d)
    ### initialize the action
    ### which will in turn use this specific plugin
    ### if configured correctly
    init = action.initialize_()
    if init:
        ### let us do our work
        contributors, scores = action.gather_()
        ### visualize and finalize gathered data
        print("Result:")
        print("contributors:\n%s" % contributors)
        print("scores:\n%s" % scores)
        ### evaluate test data
        if len(contributors) == len(scores):
            success = True
    ### Done
    return success


if __name__ == "__main__":
    assert test() == True
