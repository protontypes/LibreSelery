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
        answer = answerStringToBool(
            prompt(
                "simulation: ",
                default=str(config.__dict__["simulation"]),
                rprompt="Simulation let you run OpenSelery without payout and coinbase tokens.",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["simulation"] = answer

        answer = answerStringToBool(
            prompt(
                "include_self: ",
                default=str(config.__dict__["include_self"]),
                rprompt="Include the target folders contributors.",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["include_self"] = answer

        answer = answerStringToBool(
            prompt(
                "include_dependencies: ",
                default=str(config.__dict__["include_dependencies"]),
                rprompt="Include the dependencies of the target folder.",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["include_dependencies"] = answer

        answer = answerStringToBool(
            prompt(
                "include_tooling_and_runtime: ",
                default=str(config.__dict__["include_tooling_and_runtime"]),
                rprompt="Include the tooling and runtime from file validator = BoolValidator()) tooling_repos.yml.",
            )
        )
        inputFeedback(answer)
        answers["include_tooling_and_runtime"] = answer

        answer = int(
            prompt(
                "min_contributions: ",
                default=str(config.__dict__["min_contributions"]),
                rprompt="Minimum contributions made to be considered.",
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["min_contributions"] = answer

        answer = int(
            prompt(
                "included_dependency_contributor: ",
                default=str(config.__dict__["included_dependency_contributor"]),
                rprompt="Number of randomly selected dependency contributors.",
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["included_dependency_contributor"] = answer

        answer = int(
            prompt(
                "uniform_weight: ",
                default=str(config.__dict__["uniform_weight"]),
                rprompt="Base weight for all included contributors.",
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["uniform_weight"] = answer

        answer = prompt(
            "weighted_git_commits_until: ",
            default=str(config.__dict__["weighted_git_commits_until"]),
            rprompt="Give weight to the last x git commits.",
        )
        inputFeedback(answer)
        answers["weighted_git_commits_until"] = answer

        answer = int(
            prompt(
                "weighted_git_commits_weight: ",
                default=str(config.__dict__["weighted_git_commits_weight"]),
                rprompt="Weight for weighted git commits.",
                validator=IntegerValidator(),
            )
        )
        inputFeedback(answer)
        answers["weighted_git_commits_weight"] = answer

        ## full_split: weighted split over all contributors
        ## random_split: random weighted split with equal payout per contributor
        options = ["full", "random"]
        answer = (
            prompt(
                "split_mode: ",
                default=str(config.__dict__["split_mode"][:-6]),
                rprompt="split mode of salery for contributors.",
                validator=WordValidator(options),
                completer=WordCompleter(options, ignore_case=True),
            ).lower()
            + "_split"
        )
        inputFeedback(answer)
        answers["split_mode"] = answer

        answer = float(
            prompt(
                "btc_per_transaction: ",
                default=str(config.__dict__["btc_per_transaction"]),
                rprompt="The amount of bitcons send per transaction.",
                validator=DecimalValidator(),
            )
        )
        inputFeedback(answer)
        answers["btc_per_transaction"] = answer

        answer = int(
            prompt(
                "number_payout_contributors_per_run: ",
                default=str(config.__dict__["number_payout_contributors_per_run"]),
                rprompt="Numbers of total contributors payout per run at random split.",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["number_payout_contributors_per_run"] = answer

        answer = float(
            prompt(
                "max_payout_per_run: ",
                default=str(config.__dict__["max_payout_per_run"]),
                rprompt="The maximum amount of payout per run that is considered for random and full split.",
                validator=DecimalValidator(),
            )
        )
        inputFeedback(answer)
        answers["max_payout_per_run"] = answer

        answer = prompt(
            "bitcoin_address: ",
            default=str(config.__dict__["bitcoin_address"]),
            rprompt="Bitcoin address to take money from for payout and take money from contributors.",
            validator=BitcoinAddressValidator(),
        )
        inputFeedback(answer)
        answers["bitcoin_address"] = answer

        answer = answerStringToBool(
            prompt(
                "check_equal_private_and_public_address: ",
                default=str(config.__dict__["check_equal_private_and_public_address"]),
                rprompt="Check that the public bitcoin address matches the secret coinbase address.",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["check_equal_private_and_public_address"] = answer

        answer = answerStringToBool(
            prompt(
                "skip_email: ",
                default=str(config.__dict__["skip_email"]),
                rprompt="Skip email sended by coinbase.",
                validator=BoolValidator(),
            )
        )
        inputFeedback(answer)
        answers["skip_email"] = answer

        answer = prompt(
            "email_note: ",
            default=str(config.__dict__["email_note"]),
            rprompt="Message send with every coinbase email. Never send an URL.",
        )
        inputFeedback(answer)
        answers["email_note"] = answer

        print("pretending to write full config:")
        print(str(answers))

        for key in answers:
            if answers[key] != config.__dict__[key]:
                print(
                    "change %s from %s to %s"
                    % (key, config.__dict__[key], answers[key])
                )

    except KeyboardInterrupt:
        print("Setup canceled, nothing is safed.")
    except EOFError:
        print("EOF reached. nothing is safed.")


if __name__ == "__main__":
    main()
