import argparse

from openselery.configuration import OpenSeleryConfig
from openselery import openselery

def runCli():
  args = _parseArgs()
  args.func(args)

def _runCommand(args):
    print("=============================")

    # apply args dict to config
    config = OpenSeleryConfig()
    config.apply(vars(args).items())
    # instantiate openselery and
    # let it initialize configurations,
    # arguments and environments
    selery = openselery.OpenSelery(config)
    # let openselery connect to
    # various APIs and servers to
    # allow data gathering
    selery.connect()
    # let openselery gather data
    # of all involved projects,
    # dependencies and contributors
    mainProjects, mainContributors, dependencyProjects, dependencyContributors = selery.gather()
    # please modify the weights
    # calculation to your need
    combined_weights, combined_contributors = selery.weight(mainProjects, mainContributors, dependencyProjects, dependencyContributors)
    # split between contributors
    # who should receive payout
    recipients = selery.split(
        combined_contributors, combined_weights)
    # let openselery use the given
    # address containing virtual currency
    # to pay out the selected contributors
    selery.payout(recipients)
    # visualize the generated transaction data
    # generates images with charts/diagram in
    # the results folder
    selery.visualize()
    # Done.
    print("=============================")

def _initCommand(args):
    print("Initializing new OpenSelery project")

    config = OpenSeleryConfig()

    config.bitcoin_address = input("Enter your public bitcoin address: ")
    if not config.bitcoin_address:
      print("Invalid bitcoin address")
      exit(-1)

    config.writeYaml("./selery.yml")

def _parseArgs():
    parser = argparse.ArgumentParser(description='openselery - Automated Funding')
    subparsers = parser.add_subparsers()

      # create the parser for the "init" command
    parser_init = subparsers.add_parser('init', help='init --help')
    parser_init.set_defaults(func = _initCommand)

    # create the parser for the "run" command
    parser_run = subparsers.add_parser('run', help='run --help')
    parser_run.add_argument("-c", "--config", required=True, dest="config_path", type=str, help="Configuration file path")
    parser_run.add_argument("-d", "--directory", required=True, type=str, help="Git directory to scan")
    parser_run.add_argument("-r", "--results_dir", required=True, type=str, help="Result directory", dest="result_dir")
    parser_run.add_argument("-t", "--tooling", required=False, type=str, help="Tooling file path", dest="tooling_path")
    parser_run.set_defaults(func = _runCommand)

    args = parser.parse_args()
    return args
