#! /usr/bin/python3

import pluginlib
import numpy as np

ACTION_PLUGIN_MODULE_PREFIX = "libreselery.contribution_action_plugins"


def normalizeR(v):
    v = np.array(v) if type(v) != np.array else v
    return v / np.sqrt(np.sum(v**2))

def normalizeSum(v):
    v = np.array(v) if type(v) != np.array else v
    ### normalize and scale vector so that its sum is 1
    return v / v.sum()

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def applyLookupDict(LOOKUP_DICT, content, targetInst):
    for k,v in content.items():
        f = LOOKUP_DICT.get(k)
        if f:
            obj = f(v)
            setattr(targetInst, k, obj)

def simpleDictRepr(obj):
    s = "%s{" % obj.__class__.__name__
    for k,v in obj.__dict__.items():
        s += "%s: %s, " % (k,v)
    return "%s}" % s


class Contributor(object):
    """docstrig for ClassName"""
    def __init__(self, d, domainRef):
        super(Contributor, self).__init__()
        self.__dict__.update(d)
        self.domain = domainRef

class ContributionDomain(object):
    """docstrig for ClassName"""
    def __init__(self, d):
        super(ContributionDomain, self).__init__()
        self.name = next(iter(d))
        content = d.get(self.name)
        #self.__dict__.update(d.get(self.name))
        ### parse other values as well
        applyLookupDict(DOMAIN_LOOKUP_TYPES, content, self)
        ### initialize our actions as well (plugin based)
        self.initialize_()

    def initialize_(self):
        ### in case we have actions, prepare plugins
        for action in self.actions:
            action.initialize_()


    def gather_(self, cachedContributors=[]):
        contributorData = {} 
        ### for each action defined
        for action in self.actions:
            ### gather whatever you have to find out who contributed what
            ### result should be a list of contributors with a score
            contributors, scores = action.gather_()
            ### we now have evaluated all contributors for this specific domain
            contributorData[action.name] = (contributors, scores)
        return contributorData

    def mangle_(self, contributorData):
        contributorScoreData = {}
        print(contributorData)
        ### merge and add all scores for each contributor
        for actionName, data in contributorData.items():
            contributors, scores = data
            for contributor, score in zip(contributors, scores):
                ### simply add up the score from contributors
                if contributor in contributorScoreData:
                    contributorScoreData[contributor] += score
                else:
                    contributorScoreData[contributor] = score
        ### return our dict (which was convenient) 
        ### back to lists because we can work with arrays better 
        blob = [*contributorScoreData.items()]
        contributors, scores = ([c for c,s in blob], [s for c,s in blob])
        return contributors, scores

    def weight_(self, contributorData):
        ### weight action scores in relation to each other
        ### this is domain specific, so WEIGHT(SUM(contributor_scores) == 1.0)

        ### sum all scores of all different actions together so that the weighting is easier
        contributors, scores = self.mangle_(contributorData)
        ### calculate weight from score (normalize)
        weights = normalizeSum(scores)

        #for contributor, score in zip(contributors, weights):
        #    weightedContributorData[contributor] = score
        return contributors, weights
            
    def __repr__(self):
        return simpleDictRepr(self)

@pluginlib.Parent('action')
class ContributionActionPlugin(object):
    def __init__(self):
        super(ContributionActionPlugin, self).__init__()
    @pluginlib.abstractmethod
    def initialize_(self, action):
        pass
    @pluginlib.abstractmethod
    def gather_(self, cachedContributors=[]):
        pass
    #@pluginlib.abstractmethod
    #def weight_(self, actionContributors):
    #    pass

class ContributionAction(object):
    def __init__(self, d):
        super(ContributionAction, self).__init__()
        self.name = next(iter(d))
        content = d.get(self.name)
        ### parse other values as well
        applyLookupDict(ACTION_LOOKUP_TYPES, content, self)
        self.plugin = None

    def initialize_(self):
        pluginName = self.type.name
        ### initialize/load module & plugin
        moduleName = "%s.%s" % (ACTION_PLUGIN_MODULE_PREFIX, pluginName)
        loader = pluginlib.PluginLoader(modules=[moduleName])
        plugins = loader.plugins
        ### instantiate plugin object 
        self.plugin = plugins.action.get(pluginName)()     ### plugins.<pluginlib.Parent>.<plugin_alias>
        ### call first relevant method
        return self.plugin.initialize_(self)

    def gather_(self, cachedContributors=[]):
        ### gather whatever you have to find out who contributed what
        ### result should be a list of contributors with a score
        if self.plugin:
            return self.plugin.gather_(cachedContributors=cachedContributors)
            

    #def weight_(self, actionContributors):
    #    ### we should now create weights from the scores
    #    ### weights should be normalized for all contributors (SUM => 1.0)
    #    if self.plugin:
    #        return self.plugin.weight_(actionContributors)

    def __repr__(self):
        return simpleDictRepr(self)


class ContributionMetric(object):
    def __init__(self, d):
        super(ContributionMetric, self).__init__()
        self.name = next(iter(d))
        content = d.get(self.name)
        self.__dict__.update(content)
        
    def __repr__(self):
        return simpleDictRepr(self)



class ContributionType(object):
    def __init__(self, name):
        super(ContributionType, self).__init__()
        self.name = name
    def __repr__(self):
        return simpleDictRepr(self)

class ContributionTarget(object):
    def __init__(self, targetStr):
        super(ContributionTarget, self).__init__()
        self.target = targetStr
    def __repr__(self):
        return simpleDictRepr(self)

DOMAIN_LOOKUP_TYPES = {
    
    "weight" :      float,
    "actions":      lambda l: [ContributionAction(d) for d in l],
}

ACTION_LOOKUP_TYPES = {
    "type":         ContributionType,
    "applies_to":   lambda l: [ContributionTarget(d) for d in l],
    "metrics":      lambda l: [ContributionMetric(d) for d in l],
}

