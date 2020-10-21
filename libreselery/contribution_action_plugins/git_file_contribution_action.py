#! /usr/bin/python3

from libreselery.configuration import LibreSeleryConfig
from libreselery.contribution_distribution_engine_types import (
    Contributor,
    ContributionAction,
    ContributionActionPlugin,
)

### Start User Imports
### specialzed plugin imports can be added here
##################################################################################
import os
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
        self.fileFilters = action.applies_to
        return True

    def onGlobalsUpdate_(self):
        """
        Overload of abstract event method which signalizes the change of the global configuration

        Parameters:
        None

        Returns:
        None
        """
        self.directory = self.getGlobals().directory

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
        self.log(scores)
        return contributors, scores

    ### Start User Methods
    ### specialzed plugin methods can be added here
    ##################################################################################

    def execGit(self):
        ### get toplevel git dir path
        ### git rev-parse --git-dir
        ###     --show-toplevel gives path without .git
        cmds = [
            "git",
            "-C %s" % self.directory, ## run command as if in -C dir 
            "rev-parse --git-dir",  ### get .git dir of toplevel repo
        ]
        cmd = " ".join(cmds)
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = ps.communicate()
        if not stderr:
            ### encode output
            projectPath = stdout.decode("utf-8").strip()
        if not projectPath:
            raise Exception("This is not a git repository!")
        ### get project information
        project = None
        cmds = [
            "git",
            "--git-dir=%s" % projectPath,
            "config",
            "--get",
            "remote.origin.url",
        ]
        cmd = " ".join(cmds)
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = ps.communicate()
        if not stderr:
            ### encode output
            project = stdout.decode("utf-8")
        if not project:
            raise Exception("This is not a git repository!")
        ### create ls command to get all files
        fileFilterStr = " ".join(
            [
                "--exclude '%s'" % contributionTarget.target
                for contributionTarget in self.fileFilters
            ]
        )
        cmds = [
            "git",
            "ls-files",
            "--directory",  ### directory to look for files
            self.directory,
            "--ignored",  ### only ls files matching the excluded files (via --exclude)
            fileFilterStr,  ### string containing patterns for all files that should be searched for
        ]
        cmd = " ".join(cmds)
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = ps.communicate()
        if not stderr:
            ### encode output
            encoded = stdout.decode("utf-8")
            fileList = encoded.split("\n")
            ### exec git blame for each file
            fileContributions = {}
            for file in fileList:
                cmd = "git blame -CCC --line-porcelain %s" % file
                ps = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                stdout, stderr = ps.communicate()
                if not stderr:
                    try:
                        ### this can fail when blaming binary files for example, we skip those
                        encoded = stdout.decode("utf-8")
                    except UnicodeDecodeError as e:
                        continue
                    ### seperate lines into array
                    lines = encoded.split("\n")
                    ### put lines through blameParser
                    fileContributorDict = self.parseBlame(lines, project)
                    ### filter out unwanted users, for example the one git blame adds
                    ### in case there are uncommitted changes
                    ###     "<not.committed.yet>", "Not Committed Yet"
                    badContributor = Contributor("Not Committed Yet", "not.committed.yet")
                    if badContributor in fileContributorDict:
                        del fileContributorDict[badContributor]
                    fileContributions[file] = fileContributorDict
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

    def parseBlame(self, lines, project):
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
            # key = author_mail
            key = Contributor(author_user, author_mail, fromProject=project)
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
                "*.py",
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
    ### emulate some global information
    ### which is used by the plugin to work properly
    config = LibreSeleryConfig({"directory": os.getcwd()})
    action.updateGlobals(config=config, connectors=None)
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
