#! /usr/bin/python3

import pluginlib
import numpy as np
import os

ACTIVITY_PLUGIN_MODULE_PREFIX = "libreselery.contribution_activity_plugins"


def splitDictKeyVals(d):
    ### split up the dicts to create contributors and weight lists
    blob = [*d.items()]
    keys, vals = ([c for c, w in blob], [w for c, w in blob])
    return keys, vals


def normalizeR(v):
    v = np.array(v) if type(v) != np.array else v
    return v / np.sqrt(np.sum(v ** 2))


def normalizeSum(v):
    v = np.array(v) if type(v) != np.array else v
    ### normalize and scale vector so that its sum is 1
    return v / v.sum()


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


def applyLookupDict(LOOKUP_DICT, content, targetInst):
    ### apply mandatory parameters
    for k, f in LOOKUP_DICT["mandatory"].items():
        v = content.get(k, None)
        if v != None:
            obj = f(v)
            setattr(targetInst, k, obj)
        else:
            raise KeyError(
                "Configuration parameter %s was not found in given config" % k
            )
    ### apply optional parameters
    for k, f in LOOKUP_DICT["optional"].items():
        expr, default = f
        v = content.get(k, None)
        if v != None:
            obj = expr(v)
            setattr(targetInst, k, obj)
        else:
            obj = default
            setattr(targetInst, k, obj)


def simpleDictRepr(obj):
    s = "%s{" % obj.__class__.__name__
    for k, v in obj.__dict__.items():
        s += "%s: %s, " % (k, v)
    return "%s}" % s


class Contributor(object):
    def __init__(self, username, email, fromProject="<Unknown Project>"):
        self.username = username
        self.email = email
        self.fromProject = fromProject

    def __repr__(self):
        return "%s <%s>" % (self.username, self.email)

    ### make this object hashable and fit for dictionary key use
    def __hash__(self):
        return hash(str(self.email))

    ### boolean operators for this object to make it fit for dict use
    def __eq__(self, other):
        # return (self.username, self.email) == (other.username, other.email)
        return self.email == other.email

    def __ne__(self, other):
        return not (self == other)


class ContributionDomain(object):
    """Container defining the group of contributors"""

    def __init__(self, d):
        super(ContributionDomain, self).__init__()
        self.name = next(iter(d))
        content = d.get(self.name)
        # self.__dict__.update(d.get(self.name))
        ### parse other values as well
        applyLookupDict(DOMAIN_LOOKUP_TYPES, content, self)
        ### initialize our activities as well (plugin based)
        self.initialize_()

    def updateGlobals(self, config=None, connectors=None):
        if config:
            self.config = config
        if connectors:
            self.connectors = connectors
        ### propagate the globals update to all activities
        for activity in self.activities:
            activity.updateGlobals(config=config, connectors=connectors)

    def initialize_(self):
        ### in case we have activities, prepare plugins
        for activity in self.activities:
            ret = activity.initialize_()
            if not ret:
                raise ImportError(
                    "ContributionActivityPlugin %s could not be initialized properly! [ret: %s]"
                    % (activity.name, ret)
                )

    def gather_(self, cachedContributors=[]):
        contributorData = {}
        ### for each activity defined
        for activity in self.activities:
            ### gather whatever you have to find out who contributed what
            ### result should be a list of contributors with a score
            contributors, scores = activity.gather_()
            ### we now have evaluated all contributors for this specific domain
            contributorData[activity.name] = (contributors, scores)
        return contributorData

    def mangle_(self, contributorData):
        contributorScoreData = {}
        ### merge and add all scores for each contributor
        for activityName, data in contributorData.items():
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
        contributors, scores = ([c for c, s in blob], [s for c, s in blob])
        return contributors, scores

    def weight_(self, contributorData):
        ### weight activities scores in relation to each other
        ### this is domain specific, so WEIGHT(SUM(contributor_scores) == 1.0)
        ### sum all scores of all different activities together so that the weighting is easier
        contributors, scores = self.mangle_(contributorData)
        ### calculate weight from score (normalize)
        weights = normalizeSum(scores)
        # for contributor, score in zip(contributors, weights):
        #    weightedContributorData[contributor] = score
        return contributors, weights

    def __repr__(self):
        return simpleDictRepr(self)


@pluginlib.Parent("activity")
class ContributionActivityPlugin(object):
    _connectors = {}
    _globals_ = None

    def __init__(self):
        super(ContributionActivityPlugin, self).__init__()
        self.debug = False

    @pluginlib.abstractmethod
    def initialize_(self, activity):
        pass

    @pluginlib.abstractmethod
    def onGlobalsUpdate_(self):
        pass

    @pluginlib.abstractmethod
    def gather_(self, cachedContributors=[]):
        pass

    def setDebug(self, debug):
        self.debug = debug

    def getDebug(self):
        return self.debug

    def setGlobals(self, d):
        self._globals_ = d

    def getGlobals(self):
        return self._globals_

    def setConnectors(self, d):
        self._connectors = d

    def getConnectors(self):
        return self._connectors

    def log(self, msg):
        if self.debug:
            print("\t[.] Plugin [%s]: %s" % (self._alias_, msg))

    @staticmethod
    def pluginNameFromFileName(filename):
        return os.path.splitext(os.path.basename(filename))[0]


class ContributionActivity(object):
    def __init__(self, d):
        super(ContributionActivity, self).__init__()
        self.name = next(iter(d))
        content = d.get(self.name)
        ### parse other values as well
        applyLookupDict(ACTIVITY_LOOKUP_TYPES, content, self)
        self.plugin = None

    def updateGlobals(self, config=None, connectors=None):
        ### provide all global configuration parameters
        ### for this plugin
        if config:
            self.config = config
            self.plugin.setGlobals(self.config)
        if connectors:
            self.connectors = connectors
            self.plugin.setConnectors(self.connectors)
        ### call the update event of the plugin to signalize the change
        self.plugin.onGlobalsUpdate_()

    def initialize_(self):
        pluginName = self.type.name
        ### initialize/load module & plugin
        moduleName = "%s.%s" % (ACTIVITY_PLUGIN_MODULE_PREFIX, pluginName)
        loader = pluginlib.PluginLoader(modules=[moduleName])
        plugins = loader.plugins
        ### instantiate and initialize our plugin object
        pluginRef = plugins.activity.get(pluginName, None)
        pluginInitSuccess = None
        if pluginRef:
            ### instantiate plugin
            self.plugin = plugins.activity.get(
                pluginName
            )()  ### plugins.<pluginlib.Parent>.<plugin_alias>
            ### dirty little debug flag set for newly instanced plugin
            ### this has to be dne in a better way but works for now
            self.plugin.setDebug(self.debug)
            ### initialize plugin
            pluginInitSuccess = self.plugin.initialize_(self)
        return pluginInitSuccess

    def gather_(self, cachedContributors=[]):
        ### gather whatever you have to find out who contributed what
        ### result should be a list of contributors with a score
        if self.plugin:
            return self.plugin.gather_(cachedContributors=cachedContributors)

    def readParam(self, key, default=None):
        val = self.params.get(key, default)
        if not val:
            init = False
            self.plugin.log(
                "<%s> value needed in activity's [%s] <params>!" % (key, self.type.name)
            )
        return val

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
    "mandatory": {
        "weight": float,
        "activities": lambda l: [ContributionActivity(d) for d in l],
    },
    "optional": {},
}

ACTIVITY_LOOKUP_TYPES = {
    "mandatory": {"type": ContributionType},
    "optional": {
        "debug": (bool, False),
        "applies_to": (lambda l: [ContributionTarget(d) for d in l], []),
        "params": (dict, {}),
        "metrics": (lambda l: [ContributionMetric(d) for d in l], []),
    },
}
