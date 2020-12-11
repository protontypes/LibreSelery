#! /usr/bin/python3

from libreselery.configuration import LibreSeleryConfig
from libreselery.commit_identifier import CommitIdentifierFromString
from libreselery import git_utils
from libreselery.contribution_distribution_engine_types import (
    Contributor,
    ContributionActivity,
    ContributionActivityPlugin,
)

### Start User Imports
### specialzed plugin imports can be added here
##################################################################################
import sys
import os
### End User Imports
##################################################################################


class Last_Contribution(ContributionActivityPlugin):
    """
    This class is a plugin containing the implementation of a single ContributorActivity.
    It is responsible for gathering contributor information and evaluating scores
    for each contributor based on configurated metrics

    Plugin description:
    This plugin does nothing special, it's just for testing and showcasing how
    to use and implement plugins in the activity lifecycle of the CDE.
    It will just return a random contributor list and some randome scores.
    """

    _alias_ = ContributionActivityPlugin.pluginNameFromFileName(__file__)

    def __init__(self):
        super(Last_Contribution, self).__init__()

    def initialize_(self, activity):
        """
        Overload of abstract method which is responsible for initializing this plugin

        Parameters:
        activity (ContributionActivity):
            activity object which contains all necessary information of what
            a contributor has to doto be scored and recognized as such

        Returns:
        bool: True if successfully initialized
        """
        self.log("INIT")
        self.contribution_since_commit = activity.readParam("contribution_since_commit")
        self.contribution_score = activity.readParam("contribution_since_commit_score")
        self.directory = self.getGlobals().directory
        return True

    def gather_(self):
        """
        Overload of abstract method which is responsible for gathering
        contributor information and scoring contributors based on the activity defined

        Parameters:
        [optional] cachedContributors (list):
            list of contributors from various external (remote) sources which had been chached earlier
            so that plugins don't need to do expensive lookups all the time

        Returns:
        tuple: (list of contributors, list of scores)
        """

        contributors = []
        scores = []
        
        commit_identifier = CommitIdentifierFromString(
            self.contribution_since_commit
        )
        self.log(commit_identifier)
        if commit_identifier:
           # self.logError(
           #     "Invalid commit identifier in 'activity_since_commit': %s" 
           #     % self.contribute_since_commit
           # )
           # raise Exception("Invalid commit identifier in 'contribute_since_commit'")

            involved_commits = git_utils.find_involved_commits(
                self.directory, commit_identifier
            )
            self.log(involved_commits)
            if involved_commits:
                # calc release weights
                self.log(
                    "Add additional weight to contributors of the last commits until %s"
                    % str(self.contribution_since_commit)
                )
                # Create a unique list of all release contribors
                contributors = [Contributor(c.author.name, c.author.email.lower()) for c in involved_commits]
                scores = [self.contribution_score for c in involved_commits] 

            #self.log("Found release contributor: " + str(len(weighted_contributor)))
            #for idx, user in enumerate(mainContributors):
            #    if user.stats.author.email.lower() in weighted_contributor:
            #        commit_weights[idx] = self.config.activity_weight
            #        self.log(
            #            "Github email matches git commit email of contributor: "
            #            + user.stats.author.login
            #        )
            #self.log("Release Weights: " + str(commit_weights))
 

        #contributors = [
        #    Contributor("kikass13", "nickfiege999@gmail.com"),
        #    Contributor("Tobias Augspurger", "ly0@protonmail.com"),
        #]
        #scores = [1337.0, 50.0]
        self.log(contributors)
        self.log(scores)
        return contributors, scores

    ### Start User Methods
    ### specialzed plugin methods can be added here
    ##################################################################################
    ###
    ### def work(self):
    ###     pass
    ###
    ### Énd User Methods
    ##################################################################################


def test():
    success = False
    print("This is a Test!")
    ### define our input configuration (activity) which normally comes from .yml configuration
    d = {
        "test_activity_id": {
            "output": True,
            ### type of activity (also the name of the plugin _alias_ used!)
            "type": ContributionActivityPlugin.pluginNameFromFileName(__file__),
            "params": {
              "contribution_since_commit": 'tag_regex:v[0-9]+\.[0-9]+\.[0-9]+',
              "contribution_since_commit_score": 10
            }
        }
    }
    ### create an activity object
    activity = ContributionActivity(d)
    ### emulate some global information
    ### which is used by the plugin to work properly
    globalCfg = LibreSeleryConfig({"directory": os.getcwd()})
    ### initialize the action
    ### which will in turn use this specific plugin
    ### if configured correctly
    init = activity.initialize_(globals=globalCfg)
    ### preparations done, lets do something
    if init:
        ### let us do our work
        contributors, scores = activity.gather_()
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
