import subprocess
import os
import re
import json
import yaml
import random
import logging
import datetime
from urlextract import URLExtract

from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_connector import CoinbaseConnector
from openselery import git_utils
from openselery import selery_utils
from openselery.visualization import visualizeTransactions


class OpenSelery(object):
    def __init__(self, config, silent=False):
        super(OpenSelery, self).__init__()
        # set our openselery project dir, which is '../../this_script'
        self.seleryDir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.silent = silent
        self.librariesIoConnector = None
        self.githubConnector = None
        self.config = config
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
        self.log("OpenSelery HEAD sha [%s]" % git_utils.get_head_sha(selerypath))
        self.log("OpenSelery last tag [%s]" % git_utils.get_lastest_tag(selerypath))

        self.log("Preparing Configuration")
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

        mainProjects = []
        mainContributors = []

        dependencyProjects = []
        dependencyContributors = []

        toolingProjects = []
        toolingContributors = []

        self.log("Gathering project information")
        print("=======================================================")
        if self.config.include_self:
            self.logWarning("Including root project '%s'" %
                            self.config.directory)

            # find official repositories
            projectUrl = git_utils.grabLocalProject(
                self.config.directory)

            localProject = self.githubConnector.grabRemoteProjectByUrl(projectUrl)
            self.log(" -- %s" % localProject)
            self.log(" -- %s" % localProject.html_url)
            #print(" -- %s" % [c.author.email for c in localContributors])

            # safe dependency information
            mainProjects.append(localProject)

            for p in mainProjects:
                # grab contributors
                mainContributor = self.githubConnector.grabRemoteProjectContributors(
                    p)
                # filter contributors
                mainContributor = selery_utils.validateContributors(
                    mainContributor, self.config.min_contributions)
                # safe contributor information
                mainContributors.extend(mainContributor)



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
                            dependencyProjects.append(gitproject)

            for p in dependencyProjects:
                # grab contributors
                depContributors = self.githubConnector.grabRemoteProjectContributors(
                p)
                # filter contributors
                depContributors = selery_utils.validateContributors(
                    depContributors, self.config.min_contributions)
            # safe contributor information
                dependencyContributors.extend(depContributors)


        if self.config.include_tooling_and_runtime and self.config.tooling_path:
            # tooling projects will be treated as dependency projects 
            self.log("Searching for tooling of project '%s' " %
                     self.config.directory)
            for toolurl in self.config.toolrepos['github']:
                toolingProject = self.githubConnector.grabRemoteProjectByUrl(
                    toolurl)
                self.log(" -- %s" % toolingProject)
                self.log(" -- %s" % toolingProject.html_url)

                # safe tooling information
                dependencyProjects.append(toolingProject)

            self.log("Gathering toolchain contributor information")

            # scan for project contributors
            for p in toolingProjects:
                # grab contributors
                toolingContributor = self.githubConnector.grabRemoteProjectContributors(
                p)
                # filter contributors
                toolingContributor = selery_utils.validateContributors(
                    toolingContributor, self.config.min_contributions)
                # safe contributor information
                dependencyContributors.extend(toolingContributor)



        print("=======================================================")

        self.logNotify("Gathered valid directory: %s" %
                       self.config.directory)
        self.logNotify("Gathered '%s' valid repositories" %
                       len(mainProjects))
        self.logNotify("Gathered '%s' valid contributors" %
                       len(mainContributors))

        self.logNotify("Gathered '%s' valid dependencies" %
                       len(dependencyProjects))
        self.logNotify("Gathered '%s' valid dependencies" %
                       len(dependencyContributors))

        self.logNotify("Gathered '%s' valid dependencies" %
                       len(toolingProjects))
        self.logNotify("Gathered '%s' valid dependencies" %
                       len(toolingContributors))


        return  mainProjects, mainContributors, dependencyProjects, dependencyContributors 

    def weight(self, mainProjects, mainContributors, dependencyProjects, dependencyContributors):

        # create uniform weights
        self.log("Start with unifrom porbability weights for contributors")
        uniform_weights = selery_utils.calculateContributorWeights(
           mainContributors, self.config.uniform_weight)
        self.log("Uniform Weights:" +str(uniform_weights))

        # create release weights
        release_weights=[0]*len(mainContributors) 
        if self.config.consider_releases:
             # calc release weights
            self.log("Add additional weight to release contributors of last " +
                    str(self.config.releases_included)+" releases")
            # Create a unique list of all release contributor
            release_contributor = git_utils.find_release_contributor(
                self.config.directory, self.config.releases_included)
            release_contributor = set(i.lower() for i in release_contributor)
            self.log("Found release contributor: "+str(len(release_contributor)))
            for idx,user in enumerate(mainContributors):
                if user.stats.author.email.lower() in release_contributor:
                    release_weights[idx]=self.config.release_weight
                    self.log("Github email address matches git email from last release: " +user.stats.author.login )
            self.log("Release Weights:" +str(release_weights))
            # considers all release contributor equal
            release_contributor = set(release_contributor)

        # sum up the two list with the same size
        main_weights = [x + y for x, y in zip(uniform_weights, release_weights)]

        self.log("Total Weights:" +str(main_weights))
        # read @user from commit
        return main_weights

    def choose(self, contributors, weights):
        recipients = []

        # chose contributors for payout
        self.log("Choosing recipients for payout")
        if len(contributors) < 1:
            self.logError("Could not find any contributors to payoff")
            raise Exception("Aborting")

        if self.config.random_split:
            self.log("Creating random split based on weights")
            recipients = random.choices(
                contributors, weights, k=self.config.number_payout_contributors_per_run)
            contributor_payout_split = [self.config.max_payout_per_run]*len(contributor_payout_split)

        elif self.config.full_split:
            self.log("Creating full split based on weights")
            recipients = contributors 
            contributor_payout_split = selery_utils.weighted_split(contributors, weights, self.config.max_payout_per_run)

        else:
            self.logError("No split method configured")
            raise Exception("Aborting")

        for recipient in recipients:
            self.log(" -- '%s': '%s' [w: %s]" % (recipient.stats.author.html_url,
                                              recipient.stats.author.login, weights[contributors.index(recipient)]))
            self.log("  > via project '%s'" % recipient.fromProject)
            self.log(" -- Payout split '%s'" % contributor_payout_split[contributors.index(recipient)])

        return recipients

    def visualize(self):
      try:
        visualizeTransactions(self.config.result_dir)
      except Exception as e:
        print("Error creating visualization", e)

    def payout(self, recipients):
        if not self.config.simulation:
            transactionFilePath = os.path.join(self.config.result_dir, "transactions.txt")
            receiptFilePath = os.path.join(self.config.result_dir, "receipt.txt")

            # check if the public address is in the privat wallet
            if self.config.check_equal_private_and_public_address:
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
            self.log("Chech account wallet balance [%s] : [%s]" % (amount, currency))

            # Create the balance badge to show on the README
            balance_badge = {
                "schemaVersion": 1,
                "label": currency,
                "message": amount,
                "color": "green"
                }

            balanceBadgePath = os.path.join(self.config.result_dir, "balance_badge.json")
            with open(balanceBadgePath, "w") as write_file:
                json.dump(balance_badge, write_file)

            native_amount, native_currency = self.coinConnector.native_balancecheck()
            self.log("Check native account wallet balance [%s] : [%s]" % (native_amount, native_currency)) 

            # Create the native balance badge to show on the README
            native_balance_badge = {
                "schemaVersion": 1,
                "label": native_currency+" @ "+datetime.datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')+" UTC" ,
                "message": native_amount,
                "color": "green"
                }

            nativeBalanceBadgePath = os.path.join(self.config.result_dir, "native_balance_badge.json")
            with open(nativeBalanceBadgePath, "w") as write_file:
                json.dump(native_balance_badge, write_file)

            # Payout via the Coinbase API
            self.log("Trying to pay out recipients")
            self.receiptStr = ""
            for contributor in recipients:
                if self.coinConnector.useremail() != contributor.stats.author.email:
                    receipt = self.coinConnector.payout(contributor.stats.author.email, self.config.btc_per_transaction,
                                                    self.config.skip_email, self._getEmailNote())
                    self.receiptStr = self.receiptStr + str(receipt)
                    self.log("Payout of [%s][%s] succeeded" % (receipt['amount']['amount'],receipt['amount']['currency']))
                else:
                    self.logWarning("Skip payout since coinbase email is equal to contributor email")
                
            with open(receiptFilePath, "a") as f:
                f.write(str(self.receiptStr))

        if self.config.simulation:
            simulatedreceiptFilePath = os.path.join(
                    self.config.result_dir, "simulated_receipt.txt")

            self.logWarning(
                    "Configuration 'simulation' is active, so NO transaction will be executed")
            for contributor in recipients:
                self.log(" -- would have been a payout of '%.10f' bitcoin to '%s'" %
                         (self.config.btc_per_transaction, contributor.stats.author.login))

                with open(simulatedreceiptFilePath, "a") as f:
                    f.write(str(recipients))


    def _getFile(self, file):
        file_path = os.path.join(self.seleryDir, file)
        if os.path.exists(file_path):
            self.log(file_path+" read")
            return file_path
        else:
            return None

    def _getEmailNote(self):
      repo_message = ""
      try:
         remote_url = git_utils.grabLocalProject(self.config.directory)
         owner_project_name = self.githubConnector.parseRemoteToOwnerProjectName(remote_url)
         repo_message = " to " + owner_project_name
      except Exception as e:
        print("Cannot detect remote url of git repo", e)

      prefix = "Thank you for your contribution" + repo_message
      postfix = "Find out more about OpenSelery at https://github.com/protontypes/openselery."
      inner = ": " + self.config.email_note if self.config.email_note else ""
      return prefix + inner + ". " + postfix

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

