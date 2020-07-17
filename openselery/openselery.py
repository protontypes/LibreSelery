import subprocess
import argparse
import os
import re
import json
import yaml
import random
import sys
import pprint
import pdb
import github
import logging
import pickle
from urlextract import URLExtract

from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_connector import CoinbaseConnector
from openselery import git_utils
from openselery import selery_utils

class OpenSeleryConfig(object):
    __default_env_template__ = {
        "libraries_api_key": 'LIBRARIES_API_KEY',
        "github_token": 'GITHUB_TOKEN',
        "coinbase_token": 'COINBASE_TOKEN',
        "coinbase_secret": 'COINBASE_SECRET',
    }
    __default_config_template__ = {
        "simulation": True,

        "include_dependencies": False,
        "include_self": True,
        "include_tooling_and_runtime": False,

        "bitcoin_address": '',
        "check_equal_privat_and_public_address": True,
        "skip_email": True,
        "email_note": 'Fresh OpenCelery Donation',
        "btc_per_transaction": 0.000002,
        "number_payout_contributors_per_run": 1,
        "total_payout_per_run": 0.000002,
        

        "min_contributions": 1,
        "consider_releases": False,
        "releases_included": 1,
        "uniform_weight": 10,
        "release_weight": 10

    }       
    __secure_config_entries__ = ["libraries_api_key", "github_token", "coinbase_token", "coinbase_secret",
                                 "coinbase_secret"]

    def __init__(self, d={}):
        super(OpenSeleryConfig, self).__init__()
        self.apply(self.__default_config_template__)
        self.apply(d)

    def apply(self, d):
        self.__dict__.update(d)

    def applyEnv(self):
        try:
            environmentDict = {
                k: os.environ[v] for k, v in self.__default_env_template__.items()}
            self.apply(environmentDict)
        except KeyError as e:
            raise KeyError("Please provide environment variable %s" % e)


    def applyYaml(self, path):
        yamlDict = yaml.safe_load(open(path))
        # ensure type of loaded config
        for k, v in yamlDict.items():
            t1, v1, t2, v2 = type(v), v, type(
                getattr(self, k)), getattr(self, k)
            if t1 != t2:
                raise ValueError("Configuration parameter '%s' has failed type check! 's'<'%s'> should be 's'<'%s'>" % (
                    k, v1, t1, v2, t2))

        # special evaluations
        if self.max_payout_per_run < self.btc_per_transaction * self.number_payout_contributors_per_run:
            raise ValueError("The specified payout amount (self.btc_per_transaction * self.number_payout_contributors_per_run) exceeds the maximum payout (max_payout_per_run)")
        self.apply(yamlDict)

        # block url in note
        extractor = URLExtract()
        if extractor.has_urls(self.email_note):
            raise ValueError("Using URLs in note not possible")


    def __repr__(self):
        # make config safe for printing
        # secureEntries = {k: "X"*len(os.environ[v]) for k, v in self.__default_env_template__.items()}
        secureEntries = {k: "X" * len(getattr(self, k))
                         for k in self.__secure_config_entries__}
        secureDict = dict(self.__dict__)
        secureDict.update(secureEntries)
        return str(" --\n%s\n --" % secureDict)


class OpenSelery(object):
    def __init__(self, silent=False):
        super(OpenSelery, self).__init__()
        # set our openselery project dir, which is '../../this_script'
        self.seleryDir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.silent = silent
        self.librariesIoConnector = None
        self.githubConnector = None
        # start initialization of configs
        self.initialize()

    def __del__(self):
        self.logNotify(
            "Feel free to visit us @ https://github.com/protontypes/openselery")
        if hasattr(self, 'receiptStr') and self.receiptStr != "":
            self.logNotify("Done")
        else:
            self.logNotify("receipt missing")
            self.logNotify("Failed!")

    def initialize(self):
        self.logNotify("Initializing OpenSelery")
        
        # return openselery version
        selerypath = os.path.realpath(__file__)
        # return openselery version
        self.log("OpenSelery HEAD sha [%s]" %
                 git_utils.get_head_sha(selerypath))
        self.log("OpenSelery last tag [%s]" %
                 git_utils.get_lastest_tag(selerypath))

        # initialize config dict with default from template
        self.log("Preparing Configuration")
        self.config = OpenSeleryConfig()
        # parse args
        self.log("Parsing arguments")
        args = self.parseArgs()
        # apply args dict to config
        self.config.apply(vars(args).items())
        # apply yaml config to our configuration if possible
        self.log("Loading configuration [%s]" % self.config.config_path)
        self.loadYaml(self.config.config_path)
        # load our readme file
        extractor = URLExtract()
        fundingPath = self._getFile("README.md")
        if fundingPath is not None:
            self.log("Loading funding file [%s] for bitcoin wallet" % fundingPath)
            mdfile = open('README.md', 'r')
            mdstring = mdfile.read()
            urls = extractor.find_urls(mdstring)
            badge_string = "https://en.cryptobadges.io/donate/"
            for url in urls:
                if badge_string in url:
                    self.config.bitcoin_address=url.split(badge_string, 1)[1]
                    self.log("Found bitcoin address [%s]" % self.config.bitcoin_address)
        else:
            self.log("Using bitcoin address from configuration file for validation check [%s]" % self.config.bitcoin_address)
        # load tooling url

        if self.config.include_tooling_and_runtime and self.config.tooling_path:
            with open(self.config.tooling_path) as f:
                self.config.toolrepos = yaml.safe_load(f)
            if self.config.toolrepos is not None:
                self.log("Tooling file loaded [%s]" % self.config.toolrepos)
            else: 
                self.log("No tooling urls found")
        else:
            self.log("Tooling not included")
            

        # load our environment variables
        self.loadEnv()
        self.logNotify("Initialized")
        self.log(str(self.getConfig()))
        

    def parseArgs(self):
        parser = argparse.ArgumentParser(
            description='openselery - Automated Funding')
        parser.add_argument("-c", "--config", required=True, dest="config_path", type=str,
                            help="Configuration file path")
        parser.add_argument("-d", "--directory", required=True,
                            type=str, help="Git directory to scan")
        parser.add_argument("-r", "--results_dir", required=True,
                            type=str, help="Result directory", dest="result_dir")
        parser.add_argument("-t", "--tooling", required=False,
                            type=str, help="Tooling file path", dest="tooling_path")
        args = parser.parse_args()
        return args

    def loadEnv(self):
        self._execCritical(lambda: self.config.applyEnv(), [])

    def loadYaml(self, path):
        self._execCritical(lambda x: self.config.applyYaml(x), [path])

    def _execCritical(self, lambdaStatement, args=[], canFail=False):
        try:
            r = lambdaStatement(*args)
        except Exception as e:
            self.logError(e)
            raise e if not canFail else e
        return r

    def connect(self):
        # establish connection to restapi services
        self.log("Establishing LibrariesIO connection")
        self.librariesIoConnector = self._execCritical(
            lambda x: LibrariesIOConnector(x), [self.config.libraries_api_key])
        self.logNotify("LibrariesIO connection established")
        self.log("Establishing Github connection")
        self.githubConnector = self._execCritical(
            lambda x: GithubConnector(x), [self.config.github_token])
        self.logNotify("Github connection established")
        if not self.config.simulation:
            self.coinConnector = CoinbaseConnector(
                self.config.coinbase_token, self.config.coinbase_secret)

    def gather(self):
        generalContributors = []
        generalProjects = []
        generalDependencies = []
        self.log("Gathering project information")
        print("=======================================================")
        if self.config.include_self:
            self.logWarning("Including local project '%s'" %
                            self.config.directory)

            # find official repositories
            projectUrl = git_utils.grabLocalProject(
                self.config.directory)

            localProject = self.githubConnector.grabRemoteProjectByUrl(projectUrl)
            self.log(" -- %s" % localProject)
            self.log(" -- %s" % localProject.html_url)
            #print(" -- %s" % [c.author.email for c in localContributors])

            # safe dependency information
            generalProjects.append(localProject)

        if self.config.include_dependencies:
            self.log("Searching for dependencies of project '%s' " %
                     self.config.directory)
            # scan for dependencies repositories
            rubyScanScriptPath = os.path.join(
                self.seleryDir, "ruby", "scan.rb")
            process = subprocess.run(["ruby", rubyScanScriptPath, "--project=%s" % self.config.directory],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # exec and evaluate stdout
            if process.returncode == 0:
                dependencies_json = json.loads(process.stdout)
            else:
                self.logError("Could not find project manifesto")
                print(process.stderr)
                raise Exception("Aborting")

            # process dependency json
            unique_dependency_dict = selery_utils.getUniqueDependencies(
                dependencies_json)
            for platform, depList in unique_dependency_dict.items():
                for dep in depList:
                    d = dep["name"]
                    r = dep["requirement"]
                    print(" -- %s: %s [%s]" % (platform, d, r))
                    libIoProject = self.librariesIoConnector.findProject(
                        platform, d)
                    print("  > %s" % ("FOUND %s" %
                                      libIoProject if libIoProject else "NOT FOUND"))
                    # gather more information for project dependency
                    if libIoProject:
                        libIoRepository = self.librariesIoConnector.findRepository(
                            libIoProject)
                        libIoDependencies = self.librariesIoConnector.findProjectDependencies(
                            libIoProject)
                        print("  > %s" %
                              [dep.project_name for dep in libIoDependencies])

                        if libIoRepository:
                            gitproject = self.githubConnector.grabRemoteProject(
                                libIoRepository.github_id)

                            # safe project / dependency information
                            generalProjects.append(gitproject)
                            generalDependencies.extend(libIoDependencies)

        if self.config.include_tooling_and_runtime and self.config.tooling_path:
            for toolurl in self.config.toolrepos['github']:
                toolingProject = self.githubConnector.grabRemoteProjectByUrl(
                    toolurl)
                self.log(" -- %s" % toolingProject)
                self.log(" -- %s" % toolingProject.html_url)

                # safe dependency information
                generalProjects.append(toolingProject)

        self.log("Gathering contributor information")
        # scan for project contributors
        for p in generalProjects:
            # grab contributors
            depContributors = self.githubConnector.grabRemoteProjectContributors(
                p)
            # filter contributors
            depContributors = selery_utils.validateContributors(
                depContributors, self.config.min_contributions)
            # safe contributor information
            generalContributors.extend(depContributors)
        print("=======================================================")

        self.logNotify("Gathered valid directory: %s" %
                       self.config.directory)
        self.logNotify("Gathered '%s' valid repositories" %
                       len(generalProjects))
        self.logNotify("Gathered '%s' valid dependencies" %
                       len(generalDependencies))
        self.logNotify("Gathered '%s' valid contributors" %
                       len(generalContributors))
        return  self.config.directory, generalProjects, generalDependencies, generalContributors

    def weight(self, contributor, local_repo, projects, deps):
    
        if self.config.consider_releases:
             # calc release weights
            self.log("Add additional weight to release contributors of last " +
                    str(self.config.releases_included)+" releases")
            # Create a unique list of all release contributor
            release_contributor = git_utils.find_release_contributor(
                local_repo, self.config.releases_included)
            release_contributor = set(i.lower() for i in release_contributor)
            self.log("Found release contributor: "+str(len(release_contributor)))
            release_weights = selery_utils.calculateContributorWeights(
                release_contributor, self.config.release_weight)

            # considers all release contributor equal
            release_contributor = set(release_contributor)

        # create uniform probability
        self.log("Start with unifrom porbability weights for contributors")
        uniform_weights = selery_utils.calculateContributorWeights(
            contributor, self.config.uniform_weight)

        # read @user from commit
        return uniform_weights

    def choose(self, contributors, repo_path, weights):
        recipients = []

        # chose contributors for payout
        self.log("Choosing recipients for payout")

        recipients = random.choices(
            contributors, weights, k=self.config.number_payout_contributors_per_run)
        for contributor in recipients:
            self.log(" -- '%s': '%s' [w: %s]" % (contributor.stats.author.html_url,
                                              contributor.stats.author.name, weights[contributors.index(contributor)]))
            self.log("  > via project '%s'" % contributor.fromProject)
        return recipients

    def payout(self, recipients):
        if not self.config.simulation:
            transactionFilePath = os.path.join(self.config.result_dir, "transactions.txt")
            receiptFilePath = os.path.join(self.config.result_dir, "receipt.txt")
            balanceBadgePath = os.path.join(self.config.result_dir, "balance_badge.json")

            # check if the public address is in the privat wallet
            if self.config.check_equal_privat_and_public_address:
                if self.coinConnector.iswalletAddress(self.config.bitcoin_address):
                    self.log("Public and privat address match")
                else:    
                    self.logError("Public address does not match wallet address")
                    raise Exception("Aborting")
                
            # Check what transactions are done on the account.
            self.log(
            "Checking transaction history of given account [%s]" % transactionFilePath)
            transactions = self.coinConnector.pastTransactions()
            with open(transactionFilePath, "w") as f:
                f.write(str(transactions))
            
            amount,currency = self.coinConnector.balancecheck()
            self.log("Chech primary account wallet balance [%s] : [%s]" % (amount, currency))

            # Create the balance badge to show on the README
            balance_badge = {
                "schemaVersion": 1,
                "label": currency,
                "message": amount,
                "color": "orange"
                }
            print(balance_badge)
            with open(balanceBadgePath, "w") as write_file:
                json.dump(balance_badge, write_file)

            self.log("Trying to pay out donations to recipients")
            self.receiptStr = ""
            for contributor in recipients:
                self.receipt = self.coinConnector.payout(contributor.stats.author.email, self.config.btc_per_transaction,
                                                    self.config.skip_email, self.config.email_note)
                
                self.receiptStr = self.receiptStr + str(self.receipt)
                self.log("Payout of [%s][%s] succeeded" % (self.receipt['amount']['amount'],self.receipt['amount']['currency']))
                
            with open(receiptFilePath, "a") as f:
                f.write(str(self.receiptStr))

        if self.config.simulation:
            simulatedreceiptFilePath = os.path.join(
                    self.config.result_dir, "simulated_receipt.txt")

            self.logWarning(
                    "Configuration 'simulation' is active, so NO transaction will be executed")
            for contributor in recipients:
                self.log(" -- would have been a payout of '%.10f' bitcoin to '%s'" %
                         (self.config.btc_per_transaction, contributor.stats.author.name))

                with open(simulatedreceiptFilePath, "a") as f:
                    f.write(str(contributor))


    def _getFile(self, file):
        file_path = os.path.join(self.seleryDir, file)
        if os.path.exists(file_path):
            self.log(file_path+" read")
            return file_path
        else:
            return None

    def getConfig(self):
        return self.config

    def log(self, msg):
        self._log(".", msg)

    def logNotify(self, msg):
        self._log("*", msg)

    def logWarning(self, msg):
        self._log("!", msg)

    def logError(self, msg):
        self._log("#", msg)

    def _log(self, sym, msg):
        if not self.silent:
            match = re.search(
                r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', msg)
            if match is not None:
                print("Do not print privat email data")
            else:
                print("[%s] %s" % (sym, msg))

