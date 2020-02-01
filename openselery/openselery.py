import subprocess
import argparse
import os
import json
import yaml
import random
import sys

from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_connector import CoinbaseConnector
from openselery import selery_utils


class OpenSeleryConfig(object):
    __default_env_template__ = {
        "libraries_api_key": 'LIBRARIES_API_KEY',
        "github_token": 'GITHUB_TOKEN',
        "coinbase_token": 'COINBASE_TOKEN',
        "coinbase_secret": 'COINBASE_SECRET',
    }
    __default_config_template__ = {
        "bitcoin_wallet": "",

        "simulation": True,
        "include_dependencies": False,
        "include_self": True,
        "include_tooling_and_runtime": False,
        "min_contributions": 1,
        "check_equal_privat_and_public_wallet": True,
        "skip_email": True,
        "email_note": "Fresh OpenCelery Donation",
        "btc_per_transaction": 0.000002,
        "contributor_payout_count": 1,
        "total_payout_per_run": 0.000002,
    }
    __secure_config_entries__ = ["libraries_api_key", "github_token", "coinbase_token", "coinbase_secret",
                                 "coinbase_secret"]

    def __init__(self, d={}):
        super(OpenSeleryConfig, self).__init__()
        self.apply(self.__default_config_template__)
        self.apply(d)

    def apply(self, d):
        self.__dict__.update(d)

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
        if not self.total_payout_per_run / self.contributor_payout_count == self.btc_per_transaction:
            raise ValueError("Payout values do not match")
        self.apply(yamlDict)

    def applyEnv(self):
        try:
            environmentDict = {
                k: os.environ[v] for k, v in self.__default_env_template__.items()}
            self.apply(environmentDict)
        except KeyError as e:
            raise KeyError("Please provide environment variable %s" % e)

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
        self.logNotify("Done")

    def initialize(self):
        self.logNotify("Initializing OpenSelery")
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
        # load our funding file
        fundingPath = self._getFile("FUNDING.yml")
        self.log("Loading funding file [%s]" % fundingPath)
        self.loadYaml(fundingPath)
        # load our environment
        self.log("Loading environment variables")
        self.loadEnv()
        self.logNotify("Initialized")
        print(self.getConfig())

    def parseArgs(self):
        parser = argparse.ArgumentParser(
            description='openselery - Automated Funding')
        parser.add_argument("-c", "--config", required=True, dest="config_path", type=str,
                            help="Configuration file path")
        parser.add_argument("-d", "--directory", required=True,
                            type=str, help="Git directory to scan")
        parser.add_argument("-r", "--results_dir", required=True,
                            type=str, help="Result directory", dest="result_dir")
        args = parser.parse_args()
        return args

    def loadYaml(self, path):
        self._execCritical(lambda x: self.config.applyYaml(x), [path])

    def loadEnv(self):
        self._execCritical(lambda: self.config.applyEnv(), [])

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
            localProject = self.githubConnector.grabLocalProject(
                self.config.directory)

            print(" -- %s" % localProject)
            print(" -- %s" % localProject.html_url)
            #print(" -- %s" % [c.author.email for c in localContributors])

            # safe dependency information
            generalProjects.append(localProject)

        if self.config.include_dependencies:
            self.log("Searching for dependencies of project '%s' " %
                     self.config.directory)
            # scan for dependencies repositories
            rubyScanScriptPath = os.path.join(
                self.seleryDir, "scripts", "scan.rb")
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

                            #print(" -- %s" % [c.author.email for c in depContributors])

                            # safe project / dependency information
                            generalProjects.append(gitproject)
                            generalDependencies.extend(libIoDependencies)

        if self.config.include_tooling_and_runtime:
            ###
            ###
            # to be implemented
            ###
            ###
            pass

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
        self.logNotify("Gathered '%s' valid repositories" %
                       len(generalProjects))
        self.logNotify("Gathered '%s' valid dependencies" %
                       len(generalDependencies))
        self.logNotify("Gathered '%s' valid contributors" %
                       len(generalContributors))
        # print(generalProjects)
        # print(generalDependencies)
        # print(generalContributors)
        return generalProjects, generalDependencies, generalContributors

    def choose(self, contributors):
        recipients = []
        # calculate probability weights
        self.log("Calculating payout chances (weights) for contributors")
        weights = selery_utils.calculateContributorWeights(contributors)
        # chose contributors for payout
        self.log("Choosing recipients for payout")
        # for i in range(len(contributors)):
        #    luckyContributor = random.choices(contributors, weights, k=1)
        #    luckyWeight = weights[contributors.index(luckyContributor[0])]
        #    recipients.append(luckyContributor)
        #    print(" -- %s [weight: %s]" % luckyContributor.author.email, luckyWeight)
        recipients = random.choices(
            contributors, weights, k=self.config.contributor_payout_count)
        for contributor in recipients:
            print(" -- '%s': '%s' [w: %s]" % (contributor.stats.author.html_url,
                                              contributor.stats.author.email, weights[contributors.index(contributor)]))
            print("  > via project '%s'" % contributor.fromProject)
        return recipients

    def payout(self, recipients):
        if not self.config.simulation:
            transactionFilePath = os.path.join(self.config.result_dir, "transactions.txt")
            receiptFilePath = os.path.join(self.config.result_dir, "receipt.txt")

            # Check what is done on the account.
            self.log(
            "Checking transaction history of given account [%s]" % transactionFilePath)
            transactions = self.coinConnector.pastTransactions()
            with open(transactionFilePath, "a") as f:
                f.write(str(transactions))

            self.log("Trying to pay out donations to recipients")

            for contributor in recipients:
                receipt = self.coinConnector.payout(contributor.stats.author.email, self.config.btc_per_transaction,
                                                    self.config.skip_email, self.config.email_note)
                with open(receiptFilePath, "a") as f:
                    f.write(str(receipt))
        if self.config.simulation:
            self.logWarning(
                    "Configuration 'simulation' is active, so NO transaction will be executed")
            for contributor in recipients:
                print(" -- would have been a payout of '%.10f' to '%s'" %
                        (self.config.btc_per_transaction, contributor.stats.author.email))

    def _getFile(self, file):
        return os.path.join(self.seleryDir, file)

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
            print("[%s] %s" % (sym, msg))
