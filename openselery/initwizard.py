#!/usr/bin/env python3
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
        if len(document.text) == 0:
            raise ValidationError(message="No input")
        if not re.fullmatch(self.pattern, document.text):
            raise ValidationError(message="Expected Boolean Value", cursor_position=0)


class IntegerValidator(Validator):
    def __init__(self, min=None, max=None):
        self.pattern = re.compile(r"[0-9]+")
        self.negativePattern = re.compile(r"[^0-9]")
        if min != None:
            self.min = min
        if max != None:
            self.max = max

    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(message="No Input")

        if not re.fullmatch(self.pattern, document.text):
            raise ValidationError(
                message="Expected Integer Here",
                cursor_position=re.search(self.negativePattern, document.text).start(0),
            )
        N = int(document.text)
        if hasattr(self, "min") and N < self.min:
            raise ValidationError(message="Number must be at least %d" % self.min)
        if hasattr(self, "max") and N > self.max:
            raise ValidationError(message="Number must be at maximum %d" % self.max)


class DecimalValidator(Validator):
    def __init__(self):
        self.pattern = re.compile(r"[0-9]+(.[0-9]+)?")

    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(message="No Input")
        if not re.fullmatch(self.pattern, document.text):
            raise ValidationError(message="Expected decimal number here")


def answerStringToBool(arg):
    return arg[0] in "tT1"


COLOR_GREEN = "\33[32m"
COLOR_YELLOW = "\33[33m"
COLOR_DEFAULT = "\33[0m"


def makeColorPrompt(arg):
    return ANSI(COLOR_YELLOW + arg + COLOR_DEFAULT + ": ")


def printQuestion(arg):
    print("\n" + COLOR_GREEN + textwrap.fill(textwrap.dedent(arg)) + COLOR_DEFAULT)


def getConfigThroughWizard():
    # print(str(config))
    config = OpenSeleryConfig()

    try:
        answers = {}
        printQuestion(
            """\
            Do you want to enable simulation? Setting `simulation` to `True`
            allows you to run OpenSelery in a try state that does not
            pay out. No Coinbase token is needed in simulation."""
        )

        answer = answerStringToBool(
            prompt(
                makeColorPrompt("simulation"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Simulation Enabled. No payout.")
        else:
            print("Simulation Disabled.")
        answers["simulation"] = answer

        # Added "You probably want to do this enabled", because asking this question in the first place could be confusing.
        printQuestion("Do you want to include contributors of the main project?")
        answer = answerStringToBool(
            prompt(
                makeColorPrompt("include_main_repository"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Including contributors of main project")
        else:
            print("Excluding contributors of main project")
        answers["include_main_repository"] = answer

        printQuestion("Do you want to include your project dependencies?")
        answer = answerStringToBool(
            prompt(
                makeColorPrompt("include_dependencies"),
                default="True",
                validator=BoolValidator(),
            )
        )
        if answer:
            print("Dependencies will be included.")
        else:
            print("Dependencies will NOT be included.")
        answers["include_dependencies"] = answer

        printQuestion(
            "Do you want to invest in your tools listed in `tooling_repos.yml`?"
        )
        answer = answerStringToBool(
            prompt(makeColorPrompt("include_tooling_and_runtime"), default="False")
        )
        if answer:
            print("Tooling and Runtime will be included.")
        else:
            print("Tooling and Runtime has been disabled from inclusion.")
        answers["include_tooling_and_runtime"] = answer

        printQuestion("How many commits does a user need to be a contributor?")
        answer = int(
            prompt(
                makeColorPrompt("min_contributions_required_payout"),
                default="1",
                validator=IntegerValidator(),
            )
        )
        print(
            "A contributor will need at least %d commits to be included for payout."
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
            "To evaluate the contribution of a user, there is a uniform weight attached equally to every contributor. What should this weight be?"
        )
        answer = int(
            prompt(
                makeColorPrompt("uniform_weight"),
                default="30",
                validator=IntegerValidator(),
            )
        )
        print("The uniform base weight is set to %d" % answer)
        answers["uniform_weight"] = answer

        printQuestion(
            "The activity of a contributor is weighted as well. How much weight do you want to set for the activity?"
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
            print("1: All commits.")
            print("2: All commits since the last version tag.")
            print("3: Last N commits.")  # last commit  # commit:HEAD~1
            ## weight for weighted git commits
            answer = prompt(
                makeColorPrompt("activity_since_commit"),
                default="1",
                validator=IntegerValidator(min=1, max=3),
            )
            if answer == "1":
                pass
            elif answer == "2":
                answers["activity_since_commit"] = "tag_regex:v?[0-9]+\.[0-9]+\.[0-9]+"
                print(
                    "Will use the following regex to find the last version tag: v?[0-9]+\.[0-9]+\.[0-9]+"
                )
            elif answer == "3":
                printQuestion("How many commits do you want to take into account?")
                answer = prompt(
                    makeColorPrompt("N"), default="1", validator=IntegerValidator()
                )
                answers["activity_since_commit"] = "commit:HEAD~" + answer
                print("Will use last " + answer + " commits")

        ## full_split: weighted split over all contributors
        ## random_split: random weighted split with equal payout per contributor
        printQuestion(
            """\
            For some payment services the fees can become significant if a
            large amount of transactions with a small amount of money
            is performed. For this use case, a random picking behavior
            for contributors has been developed. This mode only pays
            out to a few randomly picked contributors instead of all
            of them. Full split mode splits all money. Possible values are:"""
        )
        print("1: full_split")
        print("2: random_split")

        options = ["full", "random"]
        answer = prompt(
            makeColorPrompt("split_strategy"),
            default="1",
            validator=IntegerValidator(min=1, max=2),
        )
        answer = [None, "full_split", "random_split"][int(answer)]
        answers["split_strategy"] = answer
        print("The split behavior has been set to " + answer)

        if answer == "random_split":
            printQuestion("How much should a picked contributor get?")
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

        printQuestion("How much should be sent in each run of OpenSelery?")
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

        printQuestion("What is the source Bitcoin address payout?")
        answer = prompt(
            makeColorPrompt("bitcoin_address"), validator=BitcoinAddressValidator(),
        )
        print("%s will be used to pay out contributors." % answer)
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
            printQuestion("What message to you want to attach in each coinbase email?")
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
