import argparse
import sys

from libreselery.configuration import LibreSeleryConfig
from libreselery import libreselery
from libreselery.initwizard import getConfigThroughWizard
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

    # initialize the CDE (Contribution Distribution Engine)
    # this also involves finding and
    # instantiating activity plugins
    selery.startEngine()

    # let libreselery gather data
    # of all involved projects,
    # dependencies and contributors
    contributors, weights = selery.run()
    # split between contributors
    # who should receive payout
    recipients, contributor_payout_split = selery.split(contributors, weights)
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

    if Path("selery.yml").exists():
        print("ERROR: config.yml file already exists: Aborting.")
        print("Either delete local selery.yml or delete run reinit.")
        sys.exit()

    # read selery.yml from libreselery, clean up all entries, and
    # use it as a template for the new selery.yml
    initConfigFile = Path(__file__).parent.parent / "selery.yml"
    configTemplate = re.sub(
        "^([\w]*: ).*$", "\\1", initConfigFile.read_text(), flags=re.MULTILINE
    )

    newConfig = getConfigThroughWizard()

    # fill `configTemplate` with entries date from the config wizard.
    for (key, value) in newConfig.items():
        pattern = "^" + key + ": $"
        span = re.search(pattern, configTemplate, flags=re.MULTILINE).span()
        value = str(value) if type(value) is Decimal else json.dumps(value)
        configTemplate = configTemplate[: span[1]] + value + configTemplate[span[1] :]

    configFile = open("./selery.yml", "wt")
    configFile.write(configTemplate)
    configFile.close()


def _reinitCommand(args):
    print(WelcomeMessage)
    if not Path("selery.yml").exists():
        print("ERROR: config.yml file does not exist: Aborting.")
        print("Please run init command first.")
        sys.exit()

    path = Path("./selery.yml")
    data = path.read_text()
    oldConfig = yaml.safe_load(data)
    LibreSeleryConfig.validateConfig(oldConfig, path)
    newConfig = getConfigThroughWizard(oldConfig)

    for (key, value) in newConfig.items():
        pattern = "^" + key + ": (.*)$"
        match = re.search(pattern, data, flags=re.MULTILINE)
        value = str(value) if type(value) is Decimal else json.dumps(value)
        if match:
            span = match.span(1)
            data = data[: span[0]] + value + data[span[1] :]
        else:
            ensureNewLine = "\n" if data[-1] != "\n" else ""
            data = "".join([data, ensureNewLine, key, ": ", value, "\n"])

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
