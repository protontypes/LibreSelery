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

config = OpenSeleryConfig()
config.applyYaml("selery.yml")


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


def main():
    print(str(config))
    try:
        answers = {}
        print("Simulation let you run OpenSelery without payout and coinbase tokens.")
        answer = answerStringToBool(
            prompt(
                "simulation: ",
                default=str(config.__dict__["simulation"]),
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["simulation"] = answer

        print("Include the target folders contributors.")
        answer = answerStringToBool(
            prompt(
                "include_main_repository: ",
                default=str(config.__dict__["include_main_repository"]),
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["include_main_repository"] = answer
        print("Include the dependencies of the target folder.")
        answer = answerStringToBool(
            prompt(
                "include_dependencies: ",
                default=str(config.__dict__["include_dependencies"]),
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["include_dependencies"] = answer
        print(
            "Include the tooling and runtime from file validator = BoolValidator()) tooling_repos.yml."
        )
        answer = answerStringToBool(
            prompt(
                "include_tooling_and_runtime: ",
                default=str(config.__dict__["include_tooling_and_runtime"]),
            )
        )
        inputFeedback(answer)
        answers["include_tooling_and_runtime"] = answer

        print("Minimum contributions made to be considered.")
        answer = int(
            prompt(
                "min_contributions_required_payout: ",
                default=str(config.__dict__["min_contributions_required_payout"]),
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["min_contributions_required_payout"] = answer

        print("Number of randomly selected dependency contributors.")
        answer = int(
            prompt(
                "included_dependency_contributor: ",
                default=str(config.__dict__["included_dependency_contributor"]),
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["included_dependency_contributor"] = answer

        print("Base weight for all included contributors.")
        answer = int(
            prompt(
                "uniform_weight: ",
                default=str(config.__dict__["uniform_weight"]),
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["uniform_weight"] = answer

        print("Give weight to the last x git commits.")
        answer = prompt(
            "activity_since_commit: ",
            default=str(config.__dict__["activity_since_commit"]),
        )
        inputFeedback(answer)
        answers["activity_since_commit"] = answer

        print("Weight for weighted git commits.")
        answer = int(
            prompt(
                "activity_weight: ",
                default=str(config.__dict__["activity_weight"]),
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["activity_weight"] = answer

        ## full_split: weighted split over all contributors
        ## random_split: random weighted split with equal payout per contributor
        print("split mode of salery for contributors.")
        options = ["full", "random"]
        answer = (
            prompt(
                "split_behavior: ",
                default=str(config.__dict__["split_behavior"][:-6]),
                validator=WordValidator(options),
                completer=WordCompleter(options, ignore_case=True),
            ).lower()
            + "_split"
        )
        inputFeedback(answer)
        answers["split_behavior"] = answer

        if answer == "random_split":
            print("The amount of bitcons send per transaction.")
            answer = float(
                prompt(
                    "btc_per_picked_contributor: ",
                    default=str(config.__dict__["btc_per_picked_contributor"]),
                    validator=DecimalValidator(),
                )
            )
            inputFeedback(answer)
            answers["btc_per_picked_contributor"] = answer

        print("Numbers of total contributors payout per run at random split.")
        answer = int(
            prompt(
                "number_payout_contributors_per_run: ",
                default=str(config.__dict__["number_payout_contributors_per_run"]),
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["number_payout_contributors_per_run"] = answer

        print(
            "The maximum amount of payout per run that is considered for random and full split."
        )
        answer = float(
            prompt(
                "payout_per_run: ",
                default=str(config.__dict__["payout_per_run"]),
                validator=DecimalValidator(),
            )
        )
        inputFeedback(answer)
        answers["payout_per_run"] = answer

        print(
            "Bitcoin address to take money from for payout and take money from contributors."
        )
        answer = prompt(
            "bitcoin_address: ",
            default=str(config.__dict__["bitcoin_address"]),
            validator=BitcoinAddressValidator(),
        )
        inputFeedback(answer)
        answers["bitcoin_address"] = answer

        print(
            "Check that the public bitcoin address matches the secret coinbase address."
        )
        answer = answerStringToBool(
            prompt(
                "perform_wallet_validation: ",
                default=str(config.__dict__["perform_wallet_validation"]),
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["perform_wallet_validation"] = answer

        print("Skip email sended by coinbase.")
        answer = answerStringToBool(
            prompt(
                "send_email_notification: ",
                default=str(config.__dict__["send_email_notification"]),
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["send_email_notification"] = answer

        print("Message send with every coinbase email. Never send an URL.")
        answer = prompt(
            "optional_email_message: ",
            default=str(config.__dict__["optional_email_message"]),
        )
        inputFeedback(answer)
        answers["optional_email_message"] = answer

        hasChanges = false
        for key in answers:
            if answers[key] != config.__dict__[key]:
                if not hasChanges:
                    print("The following changes have been made:")
                    hasChanges = true
                print(
                    "change %s from %s to %s"
                    % (key, config.__dict__[key], answers[key])
                )
        if not hasChanges:
            print("using default configuration")

    except KeyboardInterrupt:
        print("Setup canceled, nothing is safed.")
    except EOFError:
        print("EOF reached. nothing is safed.")


if __name__ == "__main__":
    main()
