import os
import yaml
from urlextract import URLExtract


class LibreSeleryConfig(object):
    __default_env_template__ = {
        "libraries_api_key": "LIBRARIES_API_KEY",
        "github_token": "GITHUB_TOKEN",
        "coinbase_token": "COINBASE_TOKEN",
        "coinbase_secret": "COINBASE_SECRET",
    }

    __default_config_template__ = {
        "contribution_domains": list,

        "simulation": bool,
        "include_dependencies": bool,
        "include_main_repository": bool,
        "include_tooling_and_runtime": bool,
        "included_dependency_contributor": int,
        "bitcoin_address": str,
        "perform_wallet_validation": bool,
        "send_email_notification": bool,
        "optional_email_message": str,
        "random_split_btc_per_picked_contributor": float,
        "random_split_picked_contributors": int,
        "payout_per_run": float,
        "min_payout_per_contributor": float,
        "split_strategy": str,
        "min_contributions_required_payout": int,
        "uniform_weight": int,
        "activity_weight": int,
        "activity_since_commit": str,
    }

    __secure_config_entries__ = [
        "libraries_api_key",
        "github_token",
        "coinbase_token",
        "coinbase_secret",
        "coinbase_secret",
    ]

    def __init__(self, d={}):
        super(LibreSeleryConfig, self).__init__()
        self.apply(d)

    def apply(self, d):
        self.__dict__.update(d)

    def finalize(self):
        ### should be called after a configuration was applied
        ### will check if all necessary configuration options are set and all types are matched
        for k, t in self.__default_config_template__.items():
            v = self.__dict__.get(k, None)
            if v == None:
                raise AttributeError(
                    "Error when finalizing config: Attribute '%s' missing" % (k)
                )
            if t != type(v):
                raise ValueError(
                    "Error when finalizing config: Attribute '%s' has wrong type" % (k)
                )

    def validateConfig(self, d, path=""):
        ### will check a given dictionary config for non relevant keys or wrong value types
        for k, v in d.items():
            type_ = self.__default_config_template__.get(k, None)
            ### check if config entry (key) is actually valid
            if type_ == None:
                raise AttributeError(
                    "Error in config: '%s'\n'%s:' Invalid attribute '%s'"
                    % (path, self.__class__.__name__, k)
                )
            ### check if type of config entry is valid
            if type(v) != type_:
                raise ValueError(
                    "Error in config: '%s'\n'%s:' Configuration parameter '%s' has failed type check! <'%s'> should be <'%s'>"
                    % (path, self.__class__.__name__, k, type(v), type_)
                )
        return True

    def applyEnv(self):
        try:
            environmentDict = {
                k: os.environ[v] for k, v in self.__default_env_template__.items()
            }
            self.apply(environmentDict)
        except KeyError as e:
            raise KeyError("Please provide environment variable %s" % e)

    def applyYaml(self, path):
        yamlDict = yaml.safe_load(open(path))
        ### ensure validity of provided yaml
        if self.validateConfig(yamlDict, path=path):
            ### apply config because it is valid
            self.apply(yamlDict)

            # special evaluations
            if (
                self.payout_per_run
                < self.random_split_btc_per_picked_contributor
                * self.random_split_picked_contributors
            ):
                raise ValueError(
                    "The specified payout amount (self.random_split_btc_per_picked_contributor * self.random_split_picked_contributors) exceeds the maximum payout (payout_per_run)"
                )

            # block url in note
            extractor = URLExtract()
            if extractor.has_urls(self.optional_email_message):
                raise ValueError("Using URLs in note not possible")

    def writeYaml(self, path):
        # TODO: fix order and add comments
        yamlString = yaml.dump(self.__dict__)
        file = open(path, "w")
        file.write(yamlString)
        file.close()

    def __repr__(self):
        # make config safe for printing
        # secureEntries = {k: "X"*len(os.environ[v]) for k, v in self.__default_env_template__.items()}
        secureEntries = {
            k: "X" * len(getattr(self, k))
            for k in self.__secure_config_entries__
            if hasattr(self, k)
        }
        secureDict = dict(self.__dict__)
        secureDict.update(secureEntries)
        return str(" --\n%s\n --" % secureDict)
