#!/usr/bin/python3
import subprocess
import argparse
import os
import json
import yaml
import re
import random
import sys

from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_pay import CoinbaseConnector
from openselery import selery_utils, calcweights


class OpenSeleryConfig(object):
    __default_env_template__ = {
        "libraries_api_key": 'LIBRARIES_API_KEY',
        "github_token": 'GITHUB_TOKEN',
        "coinbase_token": 'COINBASE_TOKEN',
        "coinbase_secret": 'COINBASE_SECRET',
    }
    __default_config_template__ = {
        "openselery_bitcoin_wallet": "",

        "dryrun": True,
        "include_dependencies": False,
        "include_self": True,
        "include_tooling_and_runtime": False,
        "min_contributions": 1,
        "check_equal_privat_and_public_wallet": True,
        "skip_email": True,
        "btc_per_transaction": 0.000002,
        "selected_contributor": 1,
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
        ### ensure type of loaded config
        for k, v in yamlDict.items():
            t1, v1, t2, v2 = type(v), v, type(getattr(self, k)), getattr(self, k)
            if t1 != t2:
                raise ValueError("Configuration parameter '%s' has failed type check! 's'<'%s'> should be 's'<'%s'>" % (
                    k, v1, t1, v2, t2))
        ### special evaluations 
        if not self.total_payout_per_run / self.selected_contributor == self.btc_per_transaction:
            raise ValueError("Payout values do not match")
        self.apply(yamlDict)

    def applyEnv(self):
        try:
            environmentDict = {k: os.environ[v] for k, v in self.__default_env_template__.items()}
            self.apply(environmentDict)
        except KeyError as e:
            raise KeyError("Please provide environment variable %s" % e)

    def __repr__(self):
        ### make config safe for printing
        # secureEntries = {k: "X"*len(os.environ[v]) for k, v in self.__default_env_template__.items()}
        secureEntries = {k: "X" * len(getattr(self, k)) for k in self.__secure_config_entries__}
        secureDict = dict(self.__dict__)
        secureDict.update(secureEntries)
        return str(secureDict)


class OpenSelery(object):
    def __init__(self, silent=False):
        super(OpenSelery, self).__init__()
        self.seleryDir = os.path.dirname(os.path.abspath(__file__))
        self.silent = silent
        self.librariesIoConnector = None
        self.githubConnector = None
        self.initialize()

    def initialize(self):
        self.logNotify("Initializing OpenSelery")
        ### initialize config dict with default from template
        self.log("Preparing Configuration")
        self.config = OpenSeleryConfig()
        ### parse args
        self.log("Parsing arguments")
        args = self.parseArgs()
        ### apply args dict to config
        self.config.apply(vars(args).items())
        ### apply yaml config to our configuration if possible
        self.log("Loading configuration [%s]" % self.config.config_path)
        self.loadYaml(self.config.config_path)
        ### load our funding file
        fundingPath = self._getFile("FUNDING.yml")
        self.log("Loading funding file [%s]" % fundingPath)
        self.loadYaml(fundingPath)
        ### load our environment
        self.log("Loading environment variables")
        self.loadEnv()
        self.logNotify("Initialized")
        print(self.getConfig())

    def parseArgs(self):
        parser = argparse.ArgumentParser(description='openselery - Automated Funding')
        parser.add_argument("-c", "--config", required=False, default=os.path.join(self.seleryDir, "openselery.yml"), dest="config_path", type=str,
                            help="Configuration file path")
        parser.add_argument("-d", "--directory", required=True, type=str, help="Git directory to scan")
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
        ### establish connection to restapi services
        self.log("Establishing LibrariesIO connection")
        self.librariesIoConnector = self._execCritical(lambda x: LibrariesIOConnector(x), [self.config.libraries_api_key])
        self.logNotify("LibrariesIO connection established")
        self.log("Establishing Github connection")
        self.githubConnector = self._execCritical(lambda x: GithubConnector(x), [self.config.github_token])
        self.logNotify("Github connection established")
        # coinConnector = CoinbaseConnector(self.config.coinbase_token, self.config.coinbase_secret)

    def dependencies(self):
        self.log("Searching for dependencies")
        projects = []

        if self.config.include_self:
            self.logWarning("Including local project '%s' as dependency" % self.config.directory)
            ### find official repositories
            project = self.githubConnector.grabLocalProject(self.config.directory)
            ### scan for project contributors
            contributors = self.githubConnector.grabRemoteProjectContributors(project)
            ### filter contributors
            contributors = selery_utils.validateContributors(contributors, self.config.min_contributions)

            print(" -- %s" % project)
            print(" -- %s" % [c.author.email for c in contributors])

        if self.config.include_dependencies:
            self.logWarning("Searching for dependencies of project '%s' " % self.config.directory)
            ### scan for dependencies repositories
            rubyScanScriptPath = os.path.join(self.seleryDir, "scripts", "scan.rb")
            process = subprocess.run(["ruby", rubyScanScriptPath, "--project=%s" % self.config.directory],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            ### exec and evaluate stdout
            if process.returncode == 0:
                dependencies_json = json.loads(process.stdout)
            else:
                self.logError("Could not find project manifesto")
                print(process.stderr)
                raise Exception("Aborting")

            print('dependencies json:')
            print(dependencies_json)
            dependencies_json = seleryutils.getUniqueDependencies(dependencies_json)

            for platform_name in dependencies_json.keys():
                if not dependencies_json[platform_name]:
                    continue
                for deps in dependencies_json[platform_name]:
                    name = deps["name"]
                    dependency = {"platform": platform_name, "name": name, "level": 1}
                    ownerandproject = librariesIO.getOwnerandProject(
                        platform_name, name)
                    if not ownerandproject:
                        continue
                    depData = librariesIO.getDependencyData(
                        ownerandproject["owner"], ownerandproject["project_name"])
                    if not depData:
                        continue
                    dependency["dependencies"] = depData["dependencies"]
                    dependency["github_id"] = depData["github_id"]

                    # gather project and user information
                    email_list = gitConnector.getContributorInfo(
                        dependency["github_id"])
                    dependency["email_list"] = email_list
                    print("Emails for " + name)
                    print("Number vaild emails entries:")
                    print(len(email_list))
                    project_list.append(dependency)

        if include_tooling_and_runtime:
            pass

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

def main():
    print("=============================")
    selery = OpenSelery()
    selery.connect()
    dependencies = selery.dependencies()
    print("=============================")


if __name__ == "__main__":
    main()
