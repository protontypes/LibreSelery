#! /usr/bin/python3

from libreselery.configuration import LibreSeleryConfig
from libreselery.github_connector import GithubConnector
from libreselery.librariesio_connector import LibrariesIOConnector
from libreselery import git_utils
from libreselery import selery_utils
from libreselery.contribution_distribution_engine_types import (
    Contributor,
    ContributionActivity,
    ContributionActivityPlugin,
)

### Start User Imports
### specialzed plugin imports can be added here
##################################################################################
import os
import subprocess
from datetime import datetime
import json
import random
### End User Imports
##################################################################################


def RANDOM_RUBY_SCANNING_SCRIPT_KAPPA(project_path): 
    return [ 
        "require 'bibliothecary'",
        "require 'json'",
        "deps = Bibliothecary.analyse('%s')" % project_path,
        "json_deps = deps.to_json",
        "puts json_deps",
    ]

class GithubDependenciesContributorsActivity(ContributionActivityPlugin):
    """
    This class is a plugin containing the implementation of a single ContributorActivity.
    It is responsible for gathering contributor information and evaluating scores
    for each contributor based on configurated metrics

    Plugin description:
    This plugin will evaluate the line-of-code contributions made from all
    contributors of local files (under git version control).
    """

    _alias_ = ContributionActivityPlugin.pluginNameFromFileName(__file__)
    GITHUB_CONNECTOR_NAME = "github"
    LIBRARIESIO_CONNECTOR_NAME = "librariesio"

    def __init__(self):
        super(GithubDependenciesContributorsActivity, self).__init__()

    def initialize_(self, activity):
        """
        Overload of abstract method which is responsible for initializing this plugin

        Parameters:
        activity (ContributionActivity):
            activity object which contains all necessary information of what
            a contributor has to doto be scored and recognized as such

        Returns:
        bool: True if successfully initialized
        """
        ### get some information about our activity
        init = True
        self.uniform_score = activity.readParam("uniform_score")
        self.min_contributions = activity.readParam("min_contributions")
        self.contributor_picks = activity.readParam("contributors_picks")
        ### get current project
        self.directory = self.getGlobals().directory

        ### get global github connector
        self.githubConnector = self.getConnectors().get(
            self.GITHUB_CONNECTOR_NAME, None
        )
        self.librariesIoConnector = self.getConnectors().get(
            self.LIBRARIESIO_CONNECTOR_NAME, None
        )
        return init

    def gather_(self):
        """
        Overload of abstract method which is responsible for gathering
        contributor information and scoring contributors based on the activity defined

        Parameters:
        [optional] cachedContributors (list):
            list of contributors from various external (remote) sources which had been chached earlier
            so that plugins don't need to do expensive lookups all the time

        Returns:
        tuple: (list of contributors, list of scores)
        """
        contributors = []
        scores = []
        if self.githubConnector and self.librariesIoConnector:
            self.log("Using '%s' as an interface to github ..." % self.githubConnector)
            projectUrl = git_utils.grabLocalProject(self.directory)

            localProject = self.githubConnector.grabRemoteProjectByUrl(projectUrl)
            self.log(
                "Gathering project information of '%s' at  local folder '%s"
                % (projectUrl, self.directory)
            )
            dependencyProjects  = self.gatherProjectDeps(localProject)
            for dep in dependencyProjects:
                cons, scrs = self.gatherProjectContributors(dep)
                self.log(cons)
                self.log(scrs)
                contributors.extend(cons)
                scores.extend(scrs)
            ### lucky pics
            if contributors and scores:
                package = zip(contributors, scores)
                lucky_picks = random.choice(package, n=self.contributor_picks)
                contributors, scores = zip(*lucky_picks)
             
        else:
            self.log(
                "Skipping work because no Connector with name '%s' could be found!"
                % self.GITHUB_CONNECTOR_NAME
            )
        self.log(contributors)
        self.log(scores)
        return contributors, scores

    ### Start User Methods
    ### specialzed plugin methods can be added here
    ##################################################################################
    ###
    def gatherProjectContributors(self, project):
        contributors = []
        #### find official repositorie
        self.log("Including contributors of project '%s'" % project.full_name)
        self.log(" -- %s" % project.html_url)
        # print(" -- %s" % [c.author.email for c in localContributors])

        ### grab contributors
        remoteContributors = self.githubConnector.grabRemoteProjectContributors(project)
        ### filter contributors
        remoteContributors = self.validateContributors(remoteContributors)
        ### extract relevant contributor information from the guthub api
        for c in remoteContributors:
            email = c.stats.author.email.lower()
            username = c.stats.author.login
            project = c.fromProject
            if email and username:
                contributors.append(Contributor(username, email, fromProject=project))
        ### calculate scores of the contributors
        ### we could dosome fancy stuff here
        ### but for now, everyone gets uniform "base" score and nothing else
        scores = [self.uniform_score for i in range(len(contributors))]
        return contributors, scores


    def gatherProjectDeps(self, project):
        ### use librariesio and stuff to gather dep urls
        project_name = project.full_name
        self.log(
            "Searching for dependencies of project '%s' " % project_name
        )
        script = "; ".join(RANDOM_RUBY_SCANNING_SCRIPT_KAPPA(self.directory))
        self.log(script)
        process = subprocess.run(
            ["ruby", "-e", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        # exec and evaluate stdout
        if process.returncode == 0:
            dependencies_json = json.loads(process.stdout)
        else:
            self.log("Could not find project manifesto")
            self.log(process.stderr)
            raise Exception("Aborting")

        # process dependency json
        unique_dependency_dict = selery_utils.getUniqueDependencies(
            dependencies_json
        )
        dependencyProjects = []
        for platform, depList in unique_dependency_dict.items():
            for dep in depList:
                d = dep["name"]
                r = dep["requirement"]
                self.log(" -- %s: %s [%s]" % (platform, d, r))
                libIoProject = self.librariesIoConnector.findProject(platform, d)
                self.log(
                    "  > %s"
                    % ("FOUND %s" % libIoProject if libIoProject else "NOT FOUND")
                )
                # gather more information for project dependency
                if libIoProject:
                    libIoRepository = self.librariesIoConnector.findRepository(
                        libIoProject
                    )
                    libIoDependencies = (
                        self.librariesIoConnector.findProjectDependencies(
                            libIoProject
                        )
                    )

                    if libIoRepository:
                        gitproject = self.githubConnector.grabRemoteProject(
                            libIoRepository.github_id
                        )

                        # safe project / dependency information
                        dependencyProjects.append(gitproject)
        self.log(
            "Gathering dependency contributor information from Github. This will take some time for larger projects."
        )
        return dependencyProjects

    def validateContributors(self, contributors):
        valid = []
        for c in contributors:
            if self.validateContributor(c, self.min_contributions):
                valid.append(c)
        return valid

    def validateContributor(self, contributor, minimum_contributions):
        if not contributor:
            return False
        # ignore contributos with less than num_contrib contributions
        if contributor.stats.total < minimum_contributions:
            return False
        # ignore contributos with no or bad email
        email = contributor.stats.author.email
        if email is None:
            return False
        elif not selery_utils.checkMail(contributor.stats.author.email):
            return False
        return True

    ###
    ### Énd User Methods
    ##################################################################################


def test_grabEnvironmentVarsFromFile(path):
    ### pip install python-dotenv
    try:
        from dotenv import load_dotenv
    except Exception as e:
        print("____________________________________________________________")
        print("Please install python-dotenv (pip install python-dotenv)")
        print("Please install python-dotenv (pip install python-dotenv)")
        print("Please install python-dotenv (pip install python-dotenv)")
        print("____________________________________________________________")
        raise
    load_dotenv(dotenv_path=path)


def test():
    success = False
    print("This is a Test!")
    ### define our input configuration (activity) which normally comes from .yml configuration
    d = {
        "contributions_from_deps": {
            "output": True,
            ### type of activity (also the name of the plugin _alias_ used!)
            "type": ContributionActivityPlugin.pluginNameFromFileName(__file__),
            "params": {
                "contributors_picks": 3,
                "min_contributions": 1,
                "uniform_score": 10,
            },
        }
    }
    ### create an activity object
    activity = ContributionActivity(d)
    ### emulate some global information
    ### which is used by the plugin to work properly
    test_grabEnvironmentVarsFromFile(
        os.path.join(os.environ["HOME"], ".libreselery/tokens.env")
    )
    myGithubToken = os.environ["GITHUB_TOKEN"]
    myLibrariesIoToken = os.environ["LIBRARIES_API_KEY"]
    connectors = {
        "github": GithubConnector(myGithubToken),
        "librariesio" : LibrariesIOConnector(myLibrariesIoToken),
    }
    globalCfg = LibreSeleryConfig(
        {
            "directory": os.path.abspath(os.path.join(os.getcwd(), "..", "..")),
        }
    )
    ### initialize the activity
    ### which will in turn use this specific plugin
    ### if configured correctly
    init = activity.initialize_(globals=globalCfg, connectors=connectors)
    if init:
        ### let us do our work
        contributors, scores = activity.gather_()
        ### visualize and finalize gathered data
        print("Result:")
        print("contributors:\n%s" % contributors)
        print("scores:\n%s" % scores)
        ### evaluate test data
        if len(contributors) == len(scores):
            success = True
    ### Done
    return success


if __name__ == "__main__":
    assert test() == True
