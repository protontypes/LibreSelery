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
from urlextract import URLExtract


from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_connector import CoinbaseConnector
from openselery import git_utils
from openselery import selery_utils

def StatusContributorRepr(self):
    result = "StatusContributor(author: "
    result += str(self.author)
    result += ", total: "
    result += str(self.total)
    result += ", weeks: "
    result += str(self.weeks)
    result += ")"
    return result

github.StatsContributor.StatsContributor.__repr__ = StatusContributorRepr

def WeekRepr(self):
    result = "Week(w: "
    result += str(self.w)
    result += ", a: "
    result += str(self.a)
    result += ", d: "
    result += str(self.d)
    result += ", c: "
    result += str(self.c)
    result += ")"
    return result

github.StatsContributor.StatsContributor.Week.__repr__ = WeekRepr


class MyPrettyPrinter(pprint.PrettyPrinter):
    def pprint_StatsContributor(self, object, stream, indent, allowance, context, level):
        pdb.set_trace()
        stream.write('StatsContributor(')
        self._format(object.author, stream, indent, allowance + 1, context, level)
        self._format(object.total, stream, indent, allowance + 1, context, level)
        self._format(object.weeks, stream, indent, allowance + 1, context, level)
        stream.write(')')

    def pprint_Week(self, object, stream, indent, allowance, context, level):
        pdb.set_trace()
        stream.write('Week(')
        self._format(object.w, stream, indent, allowance + 1, context, level)
        self._format(object.a, stream, indent, allowance + 1, context, level)
        self._format(object.d, stream, indent, allowance + 1, context, level)
        self._format(object.c, stream, indent, allowance + 1, context, level)
        stream.write(')')

    def __init__(self):
        super(MyPrettyPrinter, self).__init__()
        self._dispatch = pprint.PrettyPrinter._dispatch.copy()
        self._dispatch[github.StatsContributor.StatsContributor.__repr__] = MyPrettyPrinter.pprint_StatsContributor
        self._dispatch[github.StatsContributor.StatsContributor.Week.__repr__] = MyPrettyPrinter.pprint_Week

class OpenSeleryConfig(object):
    __default_env_template__ = {
        "libraries_api_key": 'LIBRARIES_API_KEY',
        "github_token": 'GITHUB_TOKEN',
        "coinbase_token": 'COINBASE_TOKEN',
        "coinbase_secret": 'COINBASE_SECRET',
    }
    __default_config_template__ = {
        "simulation": True,
        "inspection": True,

        "include_dependencies": False,
        "include_self": True,
        "include_tooling_and_runtime": False,

        "ethereum_address": "",
        "check_equal_privat_and_public_address": True,
        "skip_email": True,
        "email_note": "Fresh OpenCelery Donation",
        "eth_per_transaction": 0.000002,
        "contributor_payout_count": 1,
        "total_payout_per_run": 0.000002,

        "min_contributions": 1,
        "releases_included": 3,
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

        # print all logs to stdout
        if self.inspection == True:
            loggingFilePath = os.path.join(
                self.result_dir, "pythonlogs.txt")
            logging.basicConfig(level=logging.DEBUG,
                                filename=loggingFilePath, filemode='a')

        # special evaluations
        if not self.total_payout_per_run / self.contributor_payout_count == self.eth_per_transaction:
            raise ValueError("Payout values do not match")
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
        fundingPath = self._getFile("README.md")
        if fundingPath is not None:
            self.log("Loading funding file [%s] for ethereum wallet" % fundingPath)
            mdfile = open('README.md', 'r')
            f = open('README.md')
            mdstring = f.read()
            extractor = URLExtract()
            urls = extractor.find_urls(mdstring)
            badges_string = "https://en.cryptobadges.io/donate/"
            for url in urls:
                if badges_string in url:
                    self.config.ethereum_address=url.split(badges_string, 1)[1]
                    self.log("Found ethereum address [%s]" % self.config.ethereum_address)
        else:
            self.log("Using ethereum wallet from configuration file [%s]" % self.config.ethereum_address)
        # load tooling url
        toolingPath = args.tooling_path
        # load our environment variables
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
        # calc release weights
        self.log("add additional weight to release contributors of last "+str(self.config.releases_included)+" releases")
        release_contributor = git_utils.find_release_contributor(
            local_repo, self.config.releases_included)

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
        return uniform_weights, release_weights

    def choose(self, contributors, repo_path, weights):
        recipients = []

        # chose contributors for payout
        self.log("Choosing recipients for payout")

        recipients = random.choices(
            contributors, weights, k=self.config.contributor_payout_count)
        for contributor in recipients:
            self.log(" -- '%s': '%s' [w: %s]" % (contributor.stats.author.html_url,
                                              contributor.stats.author.name, weights[contributors.index(contributor)]))
            self.log("  > via project '%s'" % contributor.fromProject)
        return recipients

    def payout(self, recipients):
        if not self.config.simulation:
            transactionFilePath = os.path.join(self.config.result_dir, "transactions.txt")
            receiptFilePath = os.path.join(self.config.result_dir, "receipt.txt")

            # check if the public address is in the privat wallet

            # Check what is done on the account.
            self.log(
            "Checking transaction history of given account [%s]" % transactionFilePath)
            transactions = self.coinConnector.pastTransactions()
            with open(transactionFilePath, "a") as f:
                f.write(str(transactions))

            self.log("Trying to pay out donations to recipients")
            self.receiptStr = ""
            for contributor in recipients:
                receipt = self.coinConnector.payout(contributor.stats.author.email, self.config.eth_per_transaction,
                                                    self.config.skip_email, self.config.email_note)
                self.receiptStr = self.receiptStr + str(self.receipt)

            with open(receiptFilePath, "w") as f:
                f.write(self.receiptStr)

        if self.config.simulation:
            self.logWarning(
                    "Configuration 'simulation' is active, so NO transaction will be executed")
            for contributor in recipients:
                self.log(" -- would have been a payout of '%.10f' ethereum to '%s'" %
                         (self.config.eth_per_transaction, contributor.stats.author.name))

    def dump(self, local_repo, projects, deps, all_related_contributors, weights, recipients):
        pp = MyPrettyPrinter()
        print("local_repo")
        pp.pprint(local_repo)
        print("projects")
        pp.pprint(projects)
        print("deps")
        pp.pprint(deps)
        print("all related contributors")
        pp.pprint(all_related_contributors)
        print("weights")
        pp.pprint(weights)
        print("recipients")
        pp.pprint(recipients)
        #pdb.set_trace()

    def _getFile(self, file):
        file_path = os.path.join(self.seleryDir, file)
        if os.path.exists(file_path):
            self.log("FUNDING.yml not found")
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

