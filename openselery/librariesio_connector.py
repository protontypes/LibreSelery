import os
import sys

from openselery import selery_utils


class Project(object):
    def __init__(self, platform, d):
        super(Project, self).__init__()
        self.__dict__.update(d)
        # special vars
        self.platform = platform
        self.owner = self.repository_url.split('/')[-2]

    def __repr__(self):
        return "%s: '%s' [%s]" % (self.name, self.repository_url, self.owner)


class Dependency(object):
    def __init__(self, d):
        super(Dependency, self).__init__()
        self.__dict__.update(d)

    def __repr__(self):
        return "%s: '%s' [%s]" % (self.platform, self.project_name, self.requirements)


class Repository(object):
    def __init__(self, d):
        super(Repository, self).__init__()
        self.__dict__.update(d)


class LibrariesIOConnector(selery_utils.Connector):
    def __init__(self, key):
        super(LibrariesIOConnector, self).__init__()
        # this import has to be here, because it will INSTANTLY search for LIBRARIES_API_KEY
        # instead of beeing actualy coded properly
        # there is no proper api for this stupid wrapper and so we do this here
        # to check for access to the library
        from pybraries.search import Search
        search = Search()
        info = search.platforms()
        if not info:
            raise ConnectionError("Could not connect to LibrariesIO")

    def findProject(self, platform, depName):
        from pybraries.search import Search
        project = None
        search = Search()
        results = search.project_search(
            filters={"keywords": depName, "manager": platform})
        # only choose first search result
        if(results):
            d = results[0]
            project = Project(platform, d)
        return project

    def findRepository(self, project):
        repository = None
        from pybraries.search import Search
        search = Search()
        # Disable stdout
        sys.stdout = open(os.devnull, 'w')
        # search for repository data
        repositoryData = search.repository(
            host="github", owner=project.owner, repo=project.name)
        # Restore stdout
        sys.stdout = sys.__stdout__
        if(repositoryData):
            repository = Repository(repositoryData)
        return repository

    def findProjectDependencies(self, project):
        dependencies = []
        from pybraries.search import Search
        search = Search()
        # Disable stdout
        sys.stdout = open(os.devnull, 'w')
        # search for repository deps
        repositoryData = search.repository_dependencies(
            host="github", owner=project.owner, repo=project.name)
        # Restore stdout
        sys.stdout = sys.__stdout__
        if(repositoryData):
            depData = repositoryData["dependencies"]
            if(depData):
                dependencies = [Dependency(dep) for dep in depData]
        return dependencies
