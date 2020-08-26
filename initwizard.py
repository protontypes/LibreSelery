#!/usr/bin/env python
"""
Example of a progress bar dialog.
"""
import os
import time
import re

from prompt_toolkit.shortcuts import progress_dialog
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter

from openselery.configuration import OpenSeleryConfig


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
            float(document.text)
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


def inputFeedback(arg):
    print("You said: %s" % str(arg))


def getConfigThroughWizard():
    # print(str(config))
    config = OpenSeleryConfig()

    try:
        answers = {}
        print(
            "Do you want to enable simulation? Setting `simulation` to `True` allows you to run OpenSelery in a try state that does not pay out real money. It will also allow you to test OpenSelery without creating any accounts or actually payout out any real money."
        )
        answer = answerStringToBool(
            prompt("simulation: ", default="True", validator=BoolValidator(),)
        )
        if answer:
            print("Simulation Enabled. No real money will be distributed.")
        else:
            print("Simulation Disabled. ")
        answers["simulation"] = answer

        # Added "You probably want to do this enabled", because asking this question in the first place could be confusing.
        print(
            "Do you want to invest money to contributors of the of the root project? You probably want to do this enabled."
        )
        answer = answerStringToBool(
            prompt(
                "include_main_repository: ", default="True", validator=BoolValidator(),
            )
        )
        if answer:
            print("Including contributors of root project")
        else:
            print("Excluding contributors of root project")
        answers["include_main_repository"] = answer

        print("Do you want to distribute money to your project dependencies?")
        answer = answerStringToBool(
            prompt("include_dependencies: ", default="True", validator=BoolValidator(),)
        )
        if answer:
            print("Dependencies will receive money.")
        else:
            print("Dependencies will NOT receive money.")
        answers["include_dependencies"] = answer

        print(
            "Do you want to invest money in your tools listed in `tooling_repos.yml`?."
        )
        answer = answerStringToBool(
            prompt("include_tooling_and_runtime: ", default="False")
        )
        inputFeedback(answer)
        answers["include_tooling_and_runtime"] = answer

        print(
            "How many contributions does a contributor need in order to be considered for payout?"
        )
        answer = int(
            prompt(
                "min_contributions_required_payout: ",
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
                    "included_dependency_contributor: ",
                    default="2",
                    validator=IntegerValidator(),
                )
            )
            print("%d contributors from the dependencies will receive money." % answer)
            answers["included_dependency_contributor"] = answer

        print(
            "To compute the contribution of a person to the project, there is a uniform weight attached equally to everybody who contributed to the project. How much should this weight be?"
        )
        answer = int(
            prompt("uniform_weight: ", default="30", validator=IntegerValidator(),)
        )
        print("The uniform base weight is set to %d", answer)
        answers["uniform_weight"] = answer

        print(
            "The activity (estimation of work) of a contributor is weighted as well. How much weight do you want to set for the activity?"
        )
        answer = int(
            prompt("activity_weight: ", default="70", validator=IntegerValidator(),)
        )
        answers["activity_weight"] = answer
        if answer == 0:
            print("The activity won't have an affect on the salery.")
        else:
            print("The activity weight is %s" % answer)
            print(
                "What activity do you want to take into consideration in payout calculation?"
            )
            print("here are some example for valid values:")
            print("tag_regex:<regex>")
            print("commit:HEAD~1")  # last commit
            print("commit:<sha>")  # specific commit
            print("commit:<branch>")  # certain branch
            print("all")
            ## weight for weighted git commits
            answer = prompt("activity_since_commit: ", default="all",)
            if answer != "all":
                answers["activity_since_commit"] = answer

        ## full_split: weighted split over all contributors
        ## random_split: random weighted split with equal payout per contributor
        print(
            "For some payment services the fees can become significant if a large amount of transactions with a small amount of money is performed. For this use case, a random picking behavior for contributors has been developed. This mode only pays out to a few randomly picked contributor instead of all contributors. Full split mode splits all money. Possible values are 'full' and 'random'."
        )
        options = ["full", "random"]
        answer = (
            prompt(
                "split_behavior: ",
                default="full",
                validator=WordValidator(options),
                completer=WordCompleter(options, ignore_case=True),
            ).lower()
            + "_split"
        )
        inputFeedback(answer)
        answers["split_behavior"] = answer

        if answer == "random_split":
            print("How much money should a picked contributor get?")
            answer = float(
                prompt(
                    "btc_per_picked_contributor: ",
                    default="0.0001",
                    validator=DecimalValidator(),
                )
            )
            answers["btc_per_picked_contributor"] = answer

            print("How many contributors should get picked at random picking?")
            answer = int(
                prompt(
                    "number_payout_contributors_per_run: ",
                    default="1",
                    validator=BoolValidator(),
                )
            )
            answers["number_payout_contributors_per_run"] = answer

        print("How much money should be send in each run of OpenSelery")
        answer = float(
            prompt("payout_per_run: ", default="0.002", validator=DecimalValidator(),)
        )
        inputFeedback(answer)
        answers["payout_per_run"] = answer

        print("What is the Bitcoin address to take money from for payout?")
        answer = prompt("bitcoin_address: ", validator=BitcoinAddressValidator(),)
        inputFeedback(answer)
        answers["bitcoin_address"] = answer

        print(
            "Should OpenSelery validate that the public bitcoin address matches the secret coinbase address?"
        )
        answer = answerStringToBool(
            prompt(
                "perform_wallet_validation: ",
                default="True",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["perform_wallet_validation"] = answer

        print("Do you want Coinbase to send notification e-mails?")
        answer = answerStringToBool(
            prompt(
                "send_email_notification: ", default="False", validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["send_email_notification"] = answer

        if answer:
            print(
                "What message to you want to attach in each coinbase email? Pleast never send an URL."
            )
            answer = prompt("optional_email_message: ", default="Have a nice day.",)
            inputFeedback(answer)
            answers["optional_email_message"] = answer

        return answers

    except KeyboardInterrupt:
        print("Setup canceled, nothing is safed.")
    except EOFError:
        print("EOF reached. nothing is safed.")


if __name__ == "__main__":
    print(str(getConfigThroughWizard()))
