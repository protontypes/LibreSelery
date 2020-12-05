#! /usr/bin/python3

from libreselery.configuration import LibreSeleryConfig
from libreselery import selery_utils
from libreselery.contribution_distribution_engine_types import (
    Contributor,
    ContributionActivity,
    ContributionActivityPlugin,
)


### Start User Imports
### specialzed plugin imports can be added here
##################################################################################
import sys
import random
import os

### End User Imports
##################################################################################

from markdown import markdownFromFile, markdown
from bs4 import BeautifulSoup, element, Tag
from pprint import pprint

import sys


class AwesomeListRubric(object):
    def __init__(self, key, rubricEntries):
        super(AwesomeListRubric, self).__init__()
        self.key = key
        self.entries = []
        # pprint(rubricEntries)
        for entry in rubricEntries:
            new = AwesomeListEntry(entry)
            if new:
                self.entries.append(new)

    def __str__(self):
        s = "%s\n" % (self.key)
        for e in self.entries:
            s += "%s" % (e)
        return s

    def __repr__(self):
        return str(self)


class AwesomeListEntry(object):
    def __init__(self, entry, depth=0):
        super(AwesomeListEntry, self).__init__()
        me, children = entry

        self.depth = depth
        htmldata = me.find("a", href=True).extract()
        self.url = htmldata["href"].strip()
        self.name = htmldata.get_text().strip()
        self.text = me.get_text().strip()

        self.children = []
        for subentry in children:
            self.children.append(AwesomeListEntry(subentry, depth=self.depth + 1))

    def __str__(self):
        s = " " * self.depth * 2 + " - %s %s [%s]\n" % (self.name, self.text, self.url)
        for child in self.children:
            s += str(child)
        return s

    def __repr__(self):
        return str(self)


class AwesomeList(object):
    def __init__(self, path):
        super().__init__()
        self.rubrics = []
        soup = self.convertFromHtml(path)
        contents, d = self.generateDict(soup)
        self.createStructure(contents, d)

    def convertFromHtml(self, path):
        html = markdown(open(path).read())
        soup = BeautifulSoup(html, features="html.parser")
        # print(soup.prettify())
        return soup

    def generateDict(self, soup):
        ### crawl though all categories and extract information
        d = self.findLists(soup)
        ### ...
        ### well specifically fetch the contents entry
        contentKey = "Contents"
        contents = d[contentKey]
        if contentKey in d:
            del d[contentKey]
        return contents, d

    def createStructure(self, contents, d):
        children = self.findListItems(contents, ignoreSubLists=True)
        for c in children:
            rubricKey = c.get_text()
            rubricEntries = d.get(rubricKey, None)
            if rubricEntries:
                entries = self.findListItems(rubricEntries)
                self.rubrics.append(AwesomeListRubric(rubricKey, entries))

    ########################################################
    def findLists(self, soup):
        d = {}
        while True:
            toc = soup.find("h2")
            if toc:
                toc.extract()  ## extract will consume the item
                aList = self.findList(soup)
                if aList:
                    d[toc.get_text()] = aList
            else:
                break
        return d

    def findList(self, parent):
        ul = parent.find("ul")
        if ul:
            ul.extract()
        return ul

    def findListItems(self, parent, ignoreSubLists=False, depth=0):
        children = parent.findChildren("li", recursive=False)
        if ignoreSubLists == False:
            tree = []
            tree.extend([(child, []) for child in children])
            for i, data in enumerate(tree):
                child, subChilds = data
                ### does this item has subitems?
                subList = self.findList(child)
                if subList:
                    ### sublist found ... now add it
                    ###recursion
                    recursiveSubLists = self.findListItems(subList, depth=depth + 2)
                    tree[i] = (child, recursiveSubLists)
                # print(" " * depth + "+" +str(tree[i]).replace("\n", ""))
            ### overwrite the normal children list with the special tupled treelist containing subs and stuff
            children = tree
        return children

    def __str__(self):
        s = ""
        for e in self.rubrics:
            s += "%s" % (e)
        return s

    def __repr__(self):
        return str(self)


######################################################################################################################################################
def validateContributors(contributors):
    valid = []
    for c in contributors:
        if validateContributor(c):
            valid.append(c)
    return valid


def validateContributor(contributor):
    if not contributor:
        return False
    # ignore contributos with no or bad email
    email = contributor.stats.author.email
    if email is None:
        return False
    elif not selery_utils.checkMail(contributor.stats.author.email):
        return False
    return True


##################################################################################################################


class AwesomeListActivityPlugin(ContributionActivityPlugin):
    """
    This class is a plugin containing the implementation of a single ContributorActivity.
    It is responsible for gathering contributor information and evaluating scores
    for each contributor based on configurated metrics

    Plugin description:
    This plugin does nothing special, it's just for testing and showcasing how
    to use and implement plugins in the activity lifecycle of the CDE.
    It will just return a random contributor list and some randome scores.
    """

    _alias_ = "awesome_list_contributors"
    GITHUB_CONNECTOR_NAME = "github"

    def __init__(self):
        super(AwesomeListActivityPlugin, self).__init__()

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
        self.log("INIT")

        ### grab global params
        self.directory = self.getGlobals().directory
        ### grab our plugin params
        self.source = os.path.join(self.directory, activity.readParam("source"))
        self.uniform_score = activity.readParam("uniform_score")
        self.random_picks = activity.readParam("randomPickCount")
        ### get global github connector
        self.githubConnector = self.getConnectors().get(
            self.GITHUB_CONNECTOR_NAME, None
        )

        return True

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

        ### lets go read an awesome list
        awesomeObject = AwesomeList(self.source)
        ### get all entries regardless of rubric and filter the ones we cant handle
        allEntries = []
        for r in awesomeObject.rubrics:
            for e in r.entries:
                url_split = e.url.split("/")
                if "github.com" in url_split[2] and url_split[4]:
                    allEntries.append(e.url)
        # self.log(allEntries)

        ### Pick random projects
        lucky_projects = random.choices(allEntries, k=self.random_picks)
        self.log(lucky_projects)

        ### grab remote project urls and validate their relevant contributors
        for url in lucky_projects:
            project = self.githubConnector.grabRemoteProjectByUrl(url)
            ### grab contributors
            remoteContributors = self.githubConnector.grabRemoteProjectContributors(
                project
            )
            ## filter contributors
            remoteContributors = validateContributors(remoteContributors)
            if remoteContributors:
                ### choose one single contributor from teh repository
                lucky_contributors = random.choices(remoteContributors, k=1)
                ### extract relevant contributor information from the github api
                for c in lucky_contributors:
                    email = c.stats.author.email.lower()
                    username = c.stats.author.login
                    project = c.fromProject
                    if email and username:
                        ### add valid and lucky contributors to our list
                        contributors.append(
                            Contributor(username, email, fromProject=project)
                        )

        ### score our contributors with fixed points
        scores = [self.uniform_score for c in contributors]
        ### done, log and return
        self.log(contributors)
        self.log(scores)
        return contributors, scores

    ### Start User Methods
    ### specialzed plugin methods can be added here
    ##################################################################################
    ###
    ### def work(self):
    ###     pass
    ###
    ### Énd User Methods
    ##################################################################################


def test():
    success = False
    print("This is a Test!")
    ### define our input configuration (activity) which normally comes from .yml configuration
    d = {
        "test_activity_id": {
            "debug": True,
            ### type of activity (also the name of the plugin _alias_ used!)
            "type": "awesome_list_contributors",
            "params": {
                "source": "AWESOME.md",
                "randomPickCount": 5,
                "uniform_score": 10,
            },
        }
    }
    ### create an activity object
    activity = ContributionActivity(d)
    ### emulate some global information
    ### which is used by the plugin to work properly
    globalCfg = LibreSeleryConfig({})
    ### initialize the action
    ### which will in turn use this specific plugin
    ### if configured correctly
    init = activity.initialize_(globals=globalCfg)
    ### preparations done, lets do something
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
