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
    ### apply and consume mandatory parameters
    for k, f in LOOKUP_DICT["mandatory"].items():
        v = content.get(k, None)
        if v != None:
            obj = f(v)
            setattr(targetInst, k, obj)
            del content[k]
        else:
            raise KeyError(
                "Configuration parameter %s was not found in given config" % k
            )
    ### apply and consume optional parameters
    for k, f in LOOKUP_DICT["optional"].items():
        expr, default = f
        v = content.get(k, None)
        if v != None:
            obj = expr(v)
            setattr(targetInst, k, obj)
            del content[k]
        else:
            obj = default
            setattr(targetInst, k, obj)
    ### check if unconsumed parameters are left,
    ### if so, it is an indicator that the user has provided
    ### a false parameter, either because of a bug or typo.
    ### We do only allow parameters defined in the respective
    ### lookup dicts [LOOKUP_DICT]
    if len(content.keys()) > 0:
        raise KeyError(
            "The Following configuration parameters could not been consumed because they do not exist! %s"
            % content
        )


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

    def initialize_(self, config, connectors):
        self.config = config
        self.connectors = connectors
        ### in case we have activities, prepare plugins
        for activity in self.activities:
            ret = activity.initialize_(globals=self.config, connectors=self.connectors)
            if not ret:
                raise ImportError(
                    "ContributionActivityPlugin '%s' could not be initialized properly! [ret: %s]"
                    % (activity.name, ret)
                )

    def gather_(self):
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
    _debug_ = False
    _output_ = False

    def __init__(self):
        super(ContributionActivityPlugin, self).__init__()

    @pluginlib.abstractmethod
    def initialize_(self, activity):
        raise NotImplementedError()

    @pluginlib.abstractmethod
    def gather_(self):
        raise NotImplementedError()

    def setOutput(self, o):
        self._output_ = o

    def getOutput(self):
        return self._output_

    def setDebug(self, debug):
        self._debug_ = debug

    def getDebug(self):
        return self._debug_

    def setGlobals(self, d):
        self._globals_ = d

    def getGlobals(self):
        return self._globals_

    def setConnectors(self, d):
        self._connectors = d

    def getConnectors(self):
        return self._connectors

    def log(self, msg):
        if self.getOutput():
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

    def initialize_(self, globals=None, connectors=None):
        # self.globals_ = globals_
        # self.connectors_ = connectors_
        ### do plugin work
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
            ### same as debug, we have to set the print option which
            ### can mute teh output of the plugin
            self.plugin.setOutput(self.output)
            ### we wil lalso set our glboals and conenctors,
            ### so tht plugins can acces those wherever
            self.plugin.setGlobals(globals)
            self.plugin.setConnectors(connectors)
            ### initialize plugin
            ### this is the first event,
            ### that the plugin user code will get
            pluginInitSuccess = self.plugin.initialize_(self)
            ### done
        return pluginInitSuccess

    def gather_(self):
        ### gather whatever you have to find out who contributed what
        ### result should be a list of contributors with a score
        if self.plugin:
            return self.plugin.gather_()

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
        "output": (bool, False),
        "applies_to": (lambda l: [ContributionTarget(d) for d in l], []),
        "params": (dict, {}),
        "metrics": (lambda l: [ContributionMetric(d) for d in l], []),
    },
}
