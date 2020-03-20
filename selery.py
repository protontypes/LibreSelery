#!/usr/bin/python3

from openselery import openselery


def main():
    print("=============================")
    # instantiate openselery and
    # let it initialize configurations,
    # arguments and environments
    selery = openselery.OpenSelery()
    # let openselery connect to
    # various APIs and servers to
    # allow data gathering
    selery.connect()
    # let openselery gather data
    # of all involved projects,
    # dependencies and contributors
    local_repo, projects, deps, all_related_contributors = selery.gather()
    # please modify the weights
    # calculation to your need
    uniform_weights = selery.weight(all_related_contributors,
                                    local_repo, projects, deps)
    # let openselery roll the dice
    # and choose some lucky contributors
    # who should receive donations
    recipients = selery.choose(
        all_related_contributors, local_repo, uniform_weights)
    # let openselery use the given
    # address containing virtual currency
    # to pay out the selected contributors
    selery.payout(recipients)
    # Dump all objects for analysing
    selery.dump(local_repo, projects, deps,
                all_related_contributors, uniform_weights, recipients)
    # Done.
    print("=============================")


if __name__ == "__main__":
    main()
