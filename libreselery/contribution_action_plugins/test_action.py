#! /usr/bin/python3

from libreselery.contribution_distribution_engine_types import ContributionActionPlugin as actionplugin


class MY_TEST_ACTION_PLUGIN_CLASS(actionplugin):
    _alias_ = 'test_action'
    
    def __init__(self):
        super(MY_TEST_ACTION_PLUGIN_CLASS, self).__init__()

    def initialize_(self, action):
        print("  > PLUGIN - INIT")
        pass

    def gather_(self, cachedContributors=[]):
        print("  > PLUGIN - GATHER")
        contributors = ["kikass13", "otherUser"]
        scores = [1337.0, 500.0]

        return contributors, scores

    #def weight_(self, actionContributors):
    #    print("  > PLUGIN - WEIGHTS")
    #    contributors = ["kikass13"]
    #    weights = [1.0]
    #    return contributors, weights
        