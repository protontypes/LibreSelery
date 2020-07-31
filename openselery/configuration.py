import os
import yaml
from urlextract import URLExtract

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
        "check_equal_private_and_public_address": True,
        "skip_email": True,
        "email_note": 'Fresh OpenCelery Donation',
        "btc_per_transaction": 0.000002,
        "number_payout_contributors_per_run": 1,
        "max_payout_per_run": 0.000002,

        "min_contributions": 1,
        "consider_releases": False,
        "releases_included": 1,
        "uniform_weight": 10,
        "release_weight": 10
    }
    __secure_config_entries__ = ["libraries_api_key", "github_token", "coinbase_token", "coinbase_secret", "coinbase_secret"]

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
