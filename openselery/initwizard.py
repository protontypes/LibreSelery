#!/usr/bin/env python
"""
Example of a progress bar dialog.
"""
import os
import time
import re
import textwrap
import curses
import pprint

from prompt_toolkit.shortcuts import progress_dialog
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import ANSI, HTML

from openselery.configuration import OpenSeleryConfig


# /usr/bin/python3
from decimal import Decimal
import requests
import json


def getBitcoinPrice():
    URL = "https://www.bitstamp.net/api/ticker/"
    try:
        r = requests.get(URL)
        return Decimal(json.loads(r.text, parse_float=Decimal)["last"])
    except requests.ConnectionError:
        return Decimal("NaN")


bitcoinPrice = getBitcoinPrice()


class BitcoinAddressValidator(Validator):
    def __init__(self):
        self.pattern = re.compile(r"(1|3|bc1)[a-zA-Z0-9]+", 0)

    def validate(self, document):
        if not re.fullmatch(self.pattern, document.text):
            raise ValidationError(message="invalid bitcoin address")
        if len(document.text) < 26:
            raise ValidationError(message="bitcoin address too short")


class BoolValidator(Validator):
    def __init__(self):
        self.pattern = re.compile(r"t(rue)?|f(alse)?|0|1", re.IGNORECASE)

    def validate(self, document):
        if not re.fullmatch(self.pattern, document.text):
            raise ValidationError(message="Expected Boolean Value", cursor_position=0)


class IntegerValidator(Validator):
    def __init__(self):
        self.pattern = re.compile(r"[0-9]+")
        self.negativePattern = re.compile(r"[^0-9]")

    def validate(self, document):
        if not re.fullmatch(self.pattern, document.text):
            if len(document.text) > 0:
                raise ValidationError(
                    message="Expected Integer Here",
                    cursor_position=re.search(
                        self.negativePattern, document.text
                    ).start(0),
                )


class DecimalValidator(Validator):
    def validate(self, document):
        try:
            Decimal(document.text)
        except ValueError:
            raise ValidationError(message="Expected decimal number here")


class WordValidator(Validator):
    def __init__(self, words):
        self.words = words

    def validate(self, document):
        if document.text not in self.words:
            raise ValidationError(message="invalid input here", cursor_position=0)


def answerStringToBool(arg):
    return arg[0] in "tT1"


COLOR_GREEN = "\33[32m"
COLOR_YELLOW = "\33[33m"
COLOR_DEFAULT = "\33[0m"


def makeColorPrompt(arg):
    return ANSI(COLOR_YELLOW + arg + COLOR_DEFAULT + ": ")


def printQuestion(arg):
    print(COLOR_GREEN + textwrap.fill(textwrap.dedent(arg)) + COLOR_DEFAULT)


def getConfigThroughWizard():
    # print(str(config))
    config = OpenSeleryConfig()

    try:
        answers = {}
        printQuestion(
            """\
            Do you want to enable simulation? Setting `simulation` to `True`
            allows you to run OpenSelery in a try state that does not
            pay out real money. It will also allow you to test
            OpenSelery without creating any accounts or actually
            payout out any real money.  """
        )

        answer = answerStringToBool(
            prompt(
                makeColorPrompt("simulation"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Simulation Enabled. No real money will be distributed.")
        else:
            print("Simulation Disabled. ")
        answers["simulation"] = answer

        # Added "You probably want to do this enabled", because asking this question in the first place could be confusing.
        printQuestion(
            "Do you want to invest money to contributors of the of the root project? You probably want to do this enabled."
        )
        answer = answerStringToBool(
            prompt(
                makeColorPrompt("include_main_repository"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Including contributors of root project")
        else:
            print("Excluding contributors of root project")
        answers["include_main_repository"] = answer

        printQuestion("Do you want to distribute money to your project dependencies?")
        answer = answerStringToBool(
            prompt(
                makeColorPrompt("include_dependencies"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Dependencies will receive money.")
        else:
            print("Dependencies will NOT receive money.")
        answers["include_dependencies"] = answer

        printQuestion(
            "Do you want to invest money in your tools listed in `tooling_repos.yml`?."
        )
        answer = answerStringToBool(
            prompt(makeColorPrompt("include_tooling_and_runtime"), default="False")
        )
        if answer:
            print("Tooling and Runtime will receive money.")
        else:
            print("Tooling and Runtime has been disabled to receive money.")
        answers["include_tooling_and_runtime"] = answer

        printQuestion(
            "How many contributions does a contributor need in order to be considered for payout?"
        )
        answer = int(
            prompt(
                makeColorPrompt("min_contributions_required_payout"),
                default="1",
                validator=IntegerValidator(),
            )
        )
        print(
            "A contributor will need at least %d contributions to be able to receive money"
            % answer
        )
        answers["min_contributions_required_payout"] = answer

        if answers["include_tooling_and_runtime"]:
            print(
                "To how many contributors of dependency projects do you want to payout money?"
            )
            answer = int(
                prompt(
                    makeColorPrompt("included_dependency_contributor"),
                    default="2",
                    validator=IntegerValidator(),
                )
            )
            print("%d contributors from the dependencies will receive money." % answer)
            answers["included_dependency_contributor"] = answer

        printQuestion(
            "To compute the contribution of a person to the project, there is a uniform weight attached equally to everybody who contributed to the project. How much should this weight be?"
        )
        answer = int(
            prompt(
                makeColorPrompt("uniform_weight"),
                default="30",
                validator=IntegerValidator(),
            )
        )
        print("The uniform base weight is set to %d", answer)
        answers["uniform_weight"] = answer

        printQuestion(
            "The activity (estimation of work) of a contributor is weighted as well. How much weight do you want to set for the activity?"
        )
        answer = int(
            prompt(
                makeColorPrompt("activity_weight"),
                default="70",
                validator=IntegerValidator(),
            )
        )
        answers["activity_weight"] = answer
        if answer == 0:
            print("The activity won't have an affect on the salary.")
        else:
            print("The activity weight is %s" % answer)
            printQuestion(
                "What activity do you want to take into consideration in payout calculation?"
            )
            print("here are some example for valid values:")
            print("tag_regex:<regex>")
            print("commit:HEAD~1")  # last commit
            print("commit:<sha>")  # specific commit
            print("commit:<branch>")  # certain branch
            print("all")
            ## weight for weighted git commits
            answer = prompt(makeColorPrompt("activity_since_commit"), default="all",)
            if answer != "all":
                answers["activity_since_commit"] = answer

        ## full_split: weighted split over all contributors
        ## random_split: random weighted split with equal payout per contributor
        printQuestion(
            """\
            For some payment services the fees can become significant if a
            large amount of transactions with a small amount of money
            is performed. For this use case, a random picking behavior
            for contributors has been developed. This mode only pays
            out to a few randomly picked contributor instead of all
            contributors. Full split mode splits all money. Possible
            values are 'full' and 'random'."""
        )

        options = ["full", "random"]
        answer = (
            prompt(
                makeColorPrompt("split_strategy"),
                default="full",
                validator=WordValidator(options),
                completer=WordCompleter(options, ignore_case=True),
            ).lower()
            + "_split"
        )
        print("The split behavior has been set to " + answer)
        answers["split_strategy"] = answer

        if answer == "random_split":
            printQuestion("How much money should a picked contributor get?")
            answer = Decimal(
                prompt(
                    makeColorPrompt("random_split_picked_contributors"),
                    default="0.0001",
                    validator=DecimalValidator(),
                )
            )
            print("Each picked contributor will receive %s BTC." % str(answer))
            print("Currently woth %s$" % str(answer * bitcoinPrice))
            answers["random_split_picked_contributors"] = answer

            printQuestion("How many contributors should get picked at random picking?")
            answer = int(
                prompt(
                    makeColorPrompt("random_split_picked_contributors"),
                    default="1",
                    validator=BoolValidator(),
                )
            )
            answers["random_split_picked_contributors"] = answer

        printQuestion("How much money should be sent in each run of OpenSelery?")
        answer = Decimal(
            prompt(
                makeColorPrompt("payout_per_run"),
                default="0.002",
                validator=DecimalValidator(),
            )
        )
        print("Each run of OpenSelery will send %s BTC" % str(answer))
        print("Currently woth %s$" % str(answer * bitcoinPrice))
        answers["payout_per_run"] = answer

        printQuestion("What should be the minimum payment per contributor?")
        answer = Decimal(
            prompt(
                makeColorPrompt("min_payout_per_contributor"),
                default="0.0",
                validator=DecimalValidator(),
            )
        )
        print("Currently woth %s$" % str(answer * bitcoinPrice))
        answers["min_payout_per_contributor"] = answer

        printQuestion(
            "How many commits should a contributor have at minimum to be picked as a contributor to receive compensation?"
        )
        answer = int(
            prompt(
                makeColorPrompt("min_contributions_required_payout"),
                default="1",
                validator=IntegerValidator(),
            )
        )
        answers["min_contributions_required_payout"] = answer

        printQuestion("What is the Bitcoin address to take money from for payout?")
        answer = prompt(
            makeColorPrompt("bitcoin_address"), validator=BitcoinAddressValidator(),
        )
        print("%s will be used to send money to contributores.")
        answers["bitcoin_address"] = answer

        printQuestion(
            "Should OpenSelery validate that the public bitcoin address matches the secret coinbase address?"
        )
        answer = answerStringToBool(
            prompt(
                makeColorPrompt("perform_wallet_validation"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Double checking of bitcoin address enabled.")
        else:
            print("Double checking of bitcoin address disabled.")
        answers["perform_wallet_validation"] = answer

        printQuestion("Do you want Coinbase to send notification e-mails?")
        answer = answerStringToBool(
            prompt(
                makeColorPrompt("send_email_notification"),
                default="False",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Email notifications will be sent.")
        else:
            print("Sending of notification emails is disabled.")
        answers["send_email_notification"] = answer

        if answer:
            print(
                "What message to you want to attach in each coinbase email? Pleast never send an URL."
            )
            answer = prompt(
                makeColorPrompt("optional_email_message"), default="Have a nice day.",
            )
            if len(answer) > 0:
                print("message in notifications: " + answer)
                answers["optional_email_message"] = answer
            else:
                print("message in notifications disabled")

        config = OpenSeleryConfig()
        config.__dict__ = answers
        return config

    except KeyboardInterrupt:
        print("Setup canceled, nothing is safed.")
    except EOFError:
        print("EOF reached. nothing is safed.")


if __name__ == "__main__":
    config = getConfigThroughWizard()
    if config:
        pprint.pprint(config.__dict__, sort_dicts=False)
