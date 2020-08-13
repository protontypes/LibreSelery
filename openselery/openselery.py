import subprocess
import os
import re
import json
import yaml
import random
import logging
import datetime

from urlextract import URLExtract
from qrcode import QRCode

from openselery.github_connector import GithubConnector
from openselery.librariesio_connector import LibrariesIOConnector
from openselery.coinbase_connector import CoinbaseConnector
from openselery import git_utils
from openselery import selery_utils
from openselery import os_utils
from openselery.visualization import visualizeTransactions


class OpenSelery(object):
    def __init__(self, config, silent=False):
        super(OpenSelery, self).__init__()
        print("=======================================================")
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
        self.logNotify("Feel free to visit us @ https://github.com/protontypes/openselery")
        print("=======================================================")

    def finish(self, receiptFilePath):
        success = True
        if receiptFilePath:
            self.logNotify("Done")
        else:
            self.logWarning("Receipt missing")
            self.logWarning("Failed!")
            success = False
        return success

    def initialize(self):
        self.logNotify("Initializing OpenSelery")

        self.seleryPackageInfo = os_utils.getPackageInfo("openselery")
        self.log("OpenSelery version [%s]" % self.seleryPackageInfo["version"])

        self.log("Preparing Configuration")
        # find all configs in potentially given config directory
        foundConfigs = []
        if(self.config.config_dir):
            for root, dirs, files in os.walk(self.config.config_dir):
                for f in files:
                    ext = os.path.splitext(f)[1]
                    if ext == ".yml" or ext == ".yaml":
                        foundConfigs.append(os.path.join(root, f))
        # group all found configs together with individually given configuration paths from user on top
        self.config.config_paths = foundConfigs + self.config.config_paths
        # apply yaml config to our configuration if possible
        self.log("Loading configurations" % self.config.config_paths)
        [print(" -- %s" % path) for path in self.config.config_paths]
        [self.loadYaml(path) for path in self.config.config_paths]

        # load the README file and check if wallet address for donation matches the configured wallet address. Before payout this address is also matched against the address of the coinbase user

        extractor = URLExtract()
        fundingPath = self._getFile("README.md")
        if fundingPath is not None:
            self.log("Loading funding file [%s] for bitcoin wallet" % fundingPath)
            mdfile = open('README.md', 'r')
            mdstring = mdfile.read()
            urls = extractor.find_urls(mdstring)
            badge_string = "https://badgen.net/badge/OpenSelery-Donation/"
            for url in urls:
                if badge_string in url:
                    self.config.bitcoin_address=url.split(badge_string, 1)[1]
                    self.log("Found bitcoin address [%s]" % self.config.bitcoin_address)
        else:
            self.log("Using bitcoin address from configuration file for validation check [%s]" % self.config.bitcoin_address)


        # Create a new QR code based on the configured wallet address 
        self.log("Creating QR Code PNG Image for Funders")
        wallet_qrcode = QRCode(error_correction=1)
        wallet_qrcode.add_data(self.config.bitcoin_address)
        wallet_qrcode.best_fit()
        wallet_qrcode.makeImpl(False,6)
        wallet_image = wallet_qrcode.make_image() 
        wallet_image.save(os.path.join(self.config.result_dir,"wallet_qrcode.png"))

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
            self.logError(str(e))
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

        projectUrl = git_utils.grabLocalProject(
           self.config.directory)

        localProject = self.githubConnector.grabRemoteProjectByUrl(projectUrl)
        self.log("Gathering project information of '%s' at  local folder '%s" % (projectUrl, self.config.directory))


        print("=======================================================")
        if self.config.include_self:
            # find official repositories
            self.log("Including contributors of root project '%s'" %
                            localProject.full_name)

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
                    localProject.full_name)
            # scan for dependencies repositories
            rubyScanScriptPath = os.path.join(self.seleryDir, "openselery", "ruby_extensions", "scan.rb")
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
                depContributors = self.githubConnector.grabRemoteProjectContributors(p)
                # filter contributors based min contribution
                depContributors = selery_utils.validateContributors(
                    depContributors, self.config.min_contributions)
            # safe contributor information
                dependencyContributors.extend(depContributors)


        if self.config.include_tooling_and_runtime and self.config.tooling_path:
            # tooling projects will be treated as dependency projects 
            self.log("Searching for tooling of project '%s' " %
                     localProject.full_name)
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
        self.logNotify("Gathered '%s' valid main repositories" %
                       len(mainProjects))
        self.logNotify("Gathered '%s' valid main contributors" %
                       len(mainContributors))

        self.logNotify("Gathered '%s' valid dependency repositories" %
                       len(dependencyProjects))
        self.logNotify("Gathered '%s' valid dependency contributors" %
                       len(dependencyContributors))

        return  mainProjects, mainContributors, dependencyProjects, dependencyContributors 

    def weight(self, mainProjects, mainContributors, dependencyProjects, dependencyContributors):

        if len(dependencyContributors):
            self.log("Add %s dependency contributor to main contributor by random choice." % self.config.included_dependency_contributor)
            randomDependencyContributors = random.choices(
                dependencyContributors, k=self.config.included_dependency_contributor)
            mainContributors.extend(randomDependencyContributors)

        # create uniform weights for all main contributors
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
                    self.log("Github email matches git commit email of release of contributor: " +user.stats.author.login )
            self.log("Release Weights: " +str(release_weights))
            # considers all release contributor equal
            release_contributor = set(release_contributor)

        # sum up the two list with the same size
        combined_weights = [x + y for x, y in zip(uniform_weights, release_weights)]

        self.log("Combined Weights: " +str(combined_weights))
        # read @user from commit
        return combined_weights, mainContributors

    def split(self, contributors, weights):
        recipients = []
        
        # chose contributors for payout
        self.log("Choosing recipients for payout")
        if len(contributors) < 1:
            self.logError("Could not find any contributors to payoff")
            raise Exception("Aborting")

        if self.config.split_mode == "random_split":
            self.log("Creating random split based on weights")
            recipients = random.choices(
                contributors, weights, k=self.config.number_payout_contributors_per_run)
            contributor_payout_split = [self.config.btc_per_transaction]*len(contributors)

        elif self.config.split_mode == "full_split":
            self.log("Creating full split based on weights")
            recipients = contributors 
            contributor_payout_split = selery_utils.weighted_split(contributors, weights, self.config.max_payout_per_run)

        else:
            self.logError("Split mode configuration unknown")
            raise Exception("Aborting")

        for recipient in recipients:
            self.log(" -- '%s': '%s' [w: %s]" % (recipient.stats.author.html_url,
                                              recipient.stats.author.login, weights[contributors.index(recipient)]))
            self.log("  > via project '%s'" % recipient.fromProject)
            self.log(" -- Payout split '%.6f'" % contributor_payout_split[contributors.index(recipient)])

        return recipients, contributor_payout_split

    def visualize(self, receiptFilePath, transactionFilePath):
        if transactionFilePath:
            self.log("Creating visualizations for past transactions [%s]" % transactionFilePath)
            try:
                visualizeTransactions(self.config.result_dir, transactionFilePath)
            except Exception as e:
                self.logError("Error creating visualization: %s" % e)

    def payout(self, recipients, contributor_payout_split):
        transactionFilePath = None
        receiptFilePath = None

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
            

            # Payout via the Coinbase API
            self.log("Trying to payout recipients")
            self.receiptStr = ""
            for idx, contributor in enumerate(recipients):
                if self.coinConnector.useremail() != contributor.stats.author.email:
                    receipt = self.coinConnector.payout(contributor.stats.author.email, '{0:.6f}'.format(contributor_payout_split[idx]).rstrip("0"), self.config.skip_email, self._getEmailNote())
                    self.receiptStr = self.receiptStr + str(receipt)
                    self.log("Payout of [%s][%s] succeeded" % (receipt['amount']['amount'],receipt['amount']['currency']))
                else:
                    self.logWarning("Skip payout since coinbase email is equal to contributor email")
                
            with open(receiptFilePath, "a") as f:
                f.write(str(self.receiptStr))

            amount,currency = self.coinConnector.balancecheck()
            self.log("Chech account wallet balance [%s] : [%s]" % (amount, currency))

            native_amount, native_currency = self.coinConnector.native_balancecheck()
            self.log("Check native account wallet balance [%s] : [%s]" % (native_amount, native_currency)) 

            self.log("Creating static badges of the wallet amount in BTC and EUR")
            # Create the balance badge to show on the README
            balance_badge = {
                "schemaVersion": 1,
                "label": currency+" - "+datetime.datetime.utcnow().strftime('%d.%-m.%Y - %H:%M:%S')+" UTC" ,
                "message": amount,
                "color": "green"
                }

            balanceBadgePath = os.path.join(self.config.result_dir, "balance_badge.json")

            with open(balanceBadgePath, "w") as write_file:
                json.dump(balance_badge, write_file)

            # Create the native balance badge to show on the README
            native_balance_badge = {
                "schemaVersion": 1,
                "label": native_currency+" - "+datetime.datetime.utcnow().strftime('%d.%-m.%Y - %H:%M:%S')+" UTC" ,
                "message": native_amount,
                "color": "green"
                }

            nativeBalanceBadgePath = os.path.join(self.config.result_dir, "native_balance_badge.json")
            with open(nativeBalanceBadgePath, "w") as write_file:
                json.dump(native_balance_badge, write_file)

        else:
            ### simulate a receipt
            receiptFilePath = os.path.join(self.config.result_dir, "simulated_receipt.txt")

            self.logWarning(
                    "Configuration 'simulation' is active, so NO transaction will be executed")
            for idx,contributor in enumerate(recipients):
                self.log(" -- would have been a payout of '%s' bitcoin to '%s'" %
                         ('{0:.6f}'.format(contributor_payout_split[idx]).rstrip("0"), contributor.stats.author.login))

            with open(receiptFilePath, "a") as f:
                f.write(str(recipients))

        return receiptFilePath, transactionFilePath


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
            match = re.search(r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', msg)
            if match is not None:
                print("Do not print privat email data")
            else:
                print("[%s] %s" % (sym, msg))

