#! /usr/bin/python3

import numpy as np

import libreselery.contribution_distribution_engine_types as cdetypes


class ContributionDistributionEngine(object):
    def __init__(self, config):
        print("\n\nLOOK, BUT DONT TOUCH!")
        super(ContributionDistributionEngine, self).__init__()
        ###grab relevant entries from selery cfg
        self.domains = self._extractContributionDomains(config)

    def _extractContributionDomains(self, config):
        ### read the config and parse usable objects for each domain configured
        domains = []
        for domainDict in config.contribution_domains:
            domain = cdetypes.ContributionDomain(domainDict)
            domains.append(domain)
        return domains

    def gather_(self):
        ### our task is to apply whatever ContributionType was configured
        ### for a specific domain and extract all
        ### contributors + their weights that fit into this domain
        print("\n\nLOOK, BUT DONT TOUCH!")
        cachedContributors = []

        contributorData = {"gather": {}}
        for domain in self.domains:
            ### execute all actions of every domain
            ### this should identify the contributos that
            ### fit the action description /
            ### that have done the configured action successfully
            contributorScores = domain.gather_(cachedContributors=cachedContributors)
            ### every domain has to weight it's actions
            contributorData["gather"][domain.name] = contributorScores
            ###
        return contributorData

    def weight_(self, contributorData):
        ### domains have to weight action scores in relation to each other
        contributorData["weight"] = {}
        for domain in self.domains:
            domainContent = contributorData.get("gather").get(domain.name)
            ### normalize contributor weights based on contributor scores
            contributors, weights = domain.weight_(domainContent)
            contributorData["weight"][domain.name] = (contributors, weights)
        return contributorData

    def merge_(self, contributorData):
        ### after all domains are processed, we now have to weight the domains
        ### in relation to each other using the "weight" attribute given
        ### via the ContributionDomain configuration
        contributorData["merge"] = {}
        for domain in self.domains:
            ### merge weights/scores of contributors over all domains
            contributors, weights = contributorData.get("weight").get(domain.name)
            for contributor, weight in zip(contributors, weights):
                if contributor in contributorData["merge"]:
                    contributorData["merge"][contributor] += weight * domain.weight
                else:
                    contributorData["merge"][contributor] = weight * domain.weight

        ### because we potentially downgraded our weights by multiplying with
        ### the given domain weight ... we have to re-normalize the weights
        ### of every contributor to be within [0 ... 1] again
        contributorData["merge_norm"] = {}
        blob = [*contributorData.get("merge").items()]
        contributors, weights = ([c for c, w in blob], [w for c, w in blob])
        newWeights = cdetypes.normalizeSum(weights)
        for contributor, weight in zip(contributors, newWeights):
            contributorData["merge_norm"][contributor] = weight
        return contributorData
