import argparse
import sys

from libreselery.configuration import LibreSeleryConfig
from libreselery import libreselery
from libreselery.initwizard import getConfigThroughWizard
from os import path
from pathlib import Path
import json, yaml
from decimal import Decimal
import re


def runCli():
    args = _parseArgs()
    args.func(args)


def _runCommand(args):
    # apply args dict to config
    config = LibreSeleryConfig()
    config.apply(vars(args).items())
    # instantiate libreselery and
    # let it initialize configurations,
    # arguments and environments
    selery = libreselery.LibreSelery(config)
    # let libreselery connect to
    # various APIs and servers to
    # allow data gathering
    selery.connect()
    # let libreselery gather data
    # of all involved projects,
    # dependencies and contributors
    (
        mainProjects,
        mainContributors,
        dependencyProjects,
        dependencyContributors,
    ) = selery.gather()
    # please modify the weights
    # calculation to your need
    combined_weights, combined_contributors = selery.weight(
        mainProjects, mainContributors, dependencyProjects, dependencyContributors
    )
    # split between contributors
    # who should receive payout
    recipients, contributor_payout_split = selery.split(
        combined_contributors, combined_weights
    )
    # let libreselery use the given
    # address containing virtual currency
    # to pay out the selected contributors
    receipt, transaction = selery.payout(recipients, contributor_payout_split)
    # visualize the generated transaction data
    # generates images with charts/diagram in
    # the results folder
    selery.visualize(receipt, transaction)
    ### finish libreselery by checking processed information
    selery.finish(receipt)
    # Done.


WelcomeMessage = """Initializing new LibreSelery project.

LibreSelery is a tool to distribute funding in free and open source
projects. This Wizard will guide you through a few question to get
your project running."""


def _initCommand(args):
    print(WelcomeMessage)

    # TODO, this should take the selery.yml from the LibreSelery
    # project to have comments.

    if path.exists("./selery.yml"):
        print("ERROR: config.yml file already exists: Aborting.")
        print("Either delete local selery.yml or delete run reinit.")
        sys.exit()

    config = getConfigThroughWizard()
    LibreSeleryConfig.validateConfig(config, "./selery.yml")
    LibreSeleryConfig(config).writeYaml("./selery.yml")


def _reinitCommand(args):
    print(WelcomeMessage)
    if not path.exists("./selery.yml"):
        print("ERROR: config.yml file does not exist: Aborting.")
        print("Pleas run init command first.")
        sys.exit()

    data = Path("./selery.yml").read_text()
    oldConfig = yaml.safe_load(data)
    newConfig = getConfigThroughWizard(oldConfig)
    # updateYaml(data, oldConfig, newConfig)

    for (key, value) in newConfig.items():
        pattern = "^" + key + ": (.*)$"
        span = re.search(pattern, data, flags=re.MULTILINE).span(1)
        value = str(value) if type(value) is Decimal else json.dumps(value)
        data = data[: span[0]] + value + data[span[1] :]

    configFile = open("./selery.yml", "wt")
    configFile.write(data)
    configFile.close()


def _parseArgs():
    parser = argparse.ArgumentParser(description="libreselery - Automated Funding")
    subparsers = parser.add_subparsers()

    # create the parser for the "init" command
    parser_init = subparsers.add_parser("init", help="init --help")
    parser_init.set_defaults(func=_initCommand)

    parser_reinit = subparsers.add_parser("reinit", help="reinit --help")
    parser_reinit.set_defaults(func=_reinitCommand)

    # create the parser for the "run" command
    parser_run = subparsers.add_parser("run", help="run --help")
    parser_run.add_argument(
        "-C",
        "--config-dir",
        required=False,
        default="",
        dest="config_dir",
        type=str,
        help="Add all configs from configuration directory",
    )
    parser_run.add_argument(
        "-c",
        "--config",
        required=False,
        dest="config_paths",
        nargs="+",
        default=[],
        help="Add configuration file path",
    )
    parser_run.add_argument(
        "-d", "--directory", required=True, type=str, help="Git directory to scan"
    )
    parser_run.add_argument(
        "-r",
        "--results_dir",
        required=True,
        type=str,
        help="Result directory",
        dest="result_dir",
    )
    parser_run.add_argument(
        "-t",
        "--tooling",
        required=False,
        type=str,
        help="Tooling file path",
        dest="tooling_path",
    )
    parser_run.set_defaults(func=_runCommand)

    args = parser.parse_args()
    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit()
    return args


if __name__ == "__main__":
    runCli()
