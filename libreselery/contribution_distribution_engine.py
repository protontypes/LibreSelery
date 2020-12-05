#! /usr/bin/python3

import numpy as np

import libreselery.contribution_distribution_engine_types as cdetypes


class ContributionDistributionEngine(object):
    def __init__(self, config, connectors):
        super(ContributionDistributionEngine, self).__init__()
        ###grab relevant entries from selery cfg
        self.domains = self._extractContributionDomains(config, connectors)

    def _extractContributionDomains(self, config, connectors):
        ### read the config and parse usable objects for each domain configured
        domains = []
        for domainDict in config.contribution_domains:
            domain = cdetypes.ContributionDomain(domainDict)
            domain.initialize_(config, connectors)
            domains.append(domain)
        return domains

    def splitDictKeyVals(self, d):
        return cdetypes.splitDictKeyVals(d)

    def gather_(self):
        ### our task is to apply whatever ContributionType was configured
        ### for a specific domain and extract all
        ### contributors + their weights that fit into this domain
        contributorDataScored = {}
        for domain in self.domains:
            ### execute all activities of every domain
            ### this should identify the contributos that
            ### fit the activity description /
            ### that have done the configured activity successfully
            contributorScores = domain.gather_()
            ### every domain has to weight it's activities
            contributorDataScored[domain.name] = contributorScores
            ###
        return contributorDataScored

    def weight_(self, contributorDataScored):
        ### domains have to weight activity scores in relation to each other
        contributorDataWeighted = {}
        for domain in self.domains:
            domainContent = contributorDataScored.get(domain.name)
            ### normalize contributor weights based on contributor scores
            contributors, weights = domain.weight_(domainContent)
            contributorDataWeighted[domain.name] = (contributors, weights)
        return contributorDataWeighted

    def merge_(self, contributorDataWeighted):
        ### after all domains are processed, we now have to weight the domains
        ### in relation to each other using the "weight" attribute given
        ### via the ContributionDomain configuration
        contributorDataMerged = {}
        for domain in self.domains:
            ### merge weights/scores of contributors over all domains
            contributors, weights = contributorDataWeighted.get(domain.name)
            for contributor, weight in zip(contributors, weights):
                if contributor in contributorDataMerged:
                    contributorDataMerged[contributor] += weight * domain.weight
                else:
                    contributorDataMerged[contributor] = weight * domain.weight
        return contributorDataMerged

    def normalize_(self, contributorDataMerged):
        ### because we potentially downgraded our weights by multiplying with
        ### the given domain weight ... we have to re-normalize the weights
        ### of every contributor to be within [0 ... 1] again
        contributorDataNormalized = {}
        contributors, weights = cdetypes.splitDictKeyVals(contributorDataMerged)
        newWeights = cdetypes.normalizeSum(weights)
        for contributor, weight in zip(contributors, newWeights):
            contributorDataNormalized[contributor] = weight
        return contributorDataNormalized
