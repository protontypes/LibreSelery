import os
import tempfile

os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp()
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from itertools import accumulate
import numpy as np
import matplotlib.dates as mdates
import json
import datetime

from libreselery.collection_utils import groupBy
from libreselery.github_connector import GithubConnector


def isoDateToDatetime(isodate):
    return datetime.datetime.strptime(isodate, "%Y-%m-%d")


def transactionToIsoDate(transaction):
    creation_date = datetime.datetime.strptime(
        transaction["created_at"], "%Y-%m-%dT%H:%M:%SZ"
    )
    return creation_date.strftime("%Y-%m-%d")


def transactionToYearMonthDay(transaction):
    creation_date = datetime.datetime.strptime(
        transaction["created_at"], "%Y-%m-%dT%H:%M:%SZ"
    )
    return creation_date.strftime("%d/%m/%Y")


def transactionToYearMonth(transaction):
    creation_date = datetime.datetime.strptime(
        transaction["created_at"], "%Y-%m-%dT%H:%M:%SZ"
    )
    return creation_date.strftime("%m/%Y")


def transactionToUser(transaction):
    userName = transaction['description']
    if not userName:
        return 'legacy'    
    if (userName.startswith('@')):
        name, _, _ = userName.partition(":")
        return name[1:]
    else:
        return 'legacy' 

def transactionToUserEmail(transaction):
    # user_name = GithubConnector.grabUserNameByEmail(transaction["to"]["email"])
    if 'transaction["to"]["email"]' in transaction:
        email = transaction["to"]["email"]
        name, _, _ = email.partition("@")
    else:
        name = "Unknown User"
    return name


def transactionIsLastMonth(transaction):
    now_date = datetime.datetime.now()
    creation_date = datetime.datetime.strptime(
        transaction["created_at"], "%Y-%m-%dT%H:%M:%SZ"
    )
    diff_date = now_date - creation_date
    return diff_date.total_seconds() <= 30 * 24 * 60 * 60


def transactionIsEur(transaction):
    return transaction["native_amount"]["currency"] == "EUR"


def transactionIsEurSpent(transaction):
    return float(transaction["native_amount"]["amount"]) < 0 and transactionIsEur(
        transaction
    )


def transactionToEur(transaction):
    assert transactionIsEur(transaction)
    return float(transaction["native_amount"]["amount"])


def transactionIsBtc(transaction):
    return transaction["amount"]["currency"] == "BTC"


def transactionToBtc(transaction):
    assert transactionIsBtc(transaction)
    return float(transaction["amount"]["amount"])


def drawBarChart(title, xlabel, keys, values):
    _, diagram = plt.subplots()
    y_pos = np.arange(len(keys))
    diagram.barh(
        y_pos,
        values,
        align="center",
        in_layout="true",
        color=(0.23137254901960785, 0.3215686274509804, 1.0),
        edgecolor="black",
    )
    diagram.set_yticks(y_pos)
    diagram.set_yticklabels(keys)
    diagram.invert_yaxis()  # labels read top-to-bottom
    diagram.set_xlabel(xlabel)
    diagram.set_title(title)
    diagram.xaxis.set_major_formatter(ScalarFormatter())


def drawEurPerUser(title, xlabel, keys, values):
    # delete legacy stuff before drawing the chart
    key_list, value_list = list(keys), list(values)
    index = key_list.index('legacy')
    del value_list[index], key_list[index]
    _, diagram = plt.subplots()
    y_pos = np.arange(30)
    diagram.barh(
        y_pos,
        value_list[:30],
        align="center",
        in_layout="true",
        color=(0.23137254901960785, 0.3215686274509804, 1.0),
        edgecolor="black",
    )
    diagram.set_yticks(y_pos)
    diagram.set_yticklabels(key_list[:30])
    diagram.invert_yaxis()  # labels read top-to-bottom
    diagram.set_xlabel(xlabel)
    diagram.set_title(title)
    diagram.xaxis.set_major_formatter(ScalarFormatter())


def drawTimeSeries(title, ylabel, keys, values):
    months = mdates.MonthLocator()
    days = mdates.DayLocator()
    months_fmt = mdates.DateFormatter("%m/%Y")

    fig, ax = plt.subplots()
    ax.plot(keys, values, color=(0.23137254901960785, 0.3215686274509804, 1.0))

    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(months_fmt)
    ax.xaxis.set_minor_locator(days)

    ax.set_xlim(min(keys), max(keys))

    ax.set_ylim(0, max(values) * 1.5)

    ax.format_xdata = months_fmt
    ax.format_ydata = lambda x: "$%1.2f" % x
    # ax.grid(True)

    ax.set_ylabel(ylabel)
    ax.set_xlabel("Time")
    ax.set_title(title)

    fig.autofmt_xdate()


def visualizeTransactions(resultDir, transactionFilePath):
    if transactionFilePath:
        # read transactions file
        with open(transactionFilePath) as transactions_file:
            transactions = json.loads(transactions_file.read())

        # prepare transaction data
        data_by_day = groupBy(
            filter(transactionIsBtc, transactions["data"]), transactionToIsoDate
        )
        spent_data_by_day_last_month = groupBy(
            filter(
                lambda t: transactionIsEurSpent(t) and transactionIsLastMonth(t),
                transactions["data"],
            ),
            transactionToYearMonthDay,
        )
        spent_data_by_year_month = groupBy(
            filter(transactionIsEurSpent, transactions["data"]), transactionToYearMonth
        )
        spent_data_by_user = groupBy(
            filter(transactionIsEurSpent, transactions["data"]), transactionToUser
        )

        wallet_balance_btc_by_day_keys = list(data_by_day.keys())
        wallet_balance_btc_by_day_keys.sort()
        wallet_balance_btc_by_day_keys_datetimes = list(
            map(
                lambda d: np.datetime64(isoDateToDatetime(d)),
                wallet_balance_btc_by_day_keys,
            )
        )
        wallet_balance_btc_by_day_values = list(
            accumulate(
                [
                    sum(map(transactionToBtc, data_by_day[k]))
                    for k in wallet_balance_btc_by_day_keys
                ]
            )
        )
        eur_by_day_last_month = {
            k: -1 * sum(map(transactionToEur, v))
            for k, v in spent_data_by_day_last_month.items()
        }
        eur_by_year_month = {
            k: -1 * sum(map(transactionToEur, v))
            for k, v in spent_data_by_year_month.items()
        }
        eur_by_user = {
            k: -1 * sum(map(transactionToEur, v)) 
            for k, v in spent_data_by_user.items()
        }
       
        # draw diagrams
        plt.rcdefaults()

        drawBarChart(
            "Transactions per day over the last month",
            "EUR",
            eur_by_day_last_month.keys(),
            eur_by_day_last_month.values(),
        )

        plt.savefig(
            os.path.join(resultDir, "transactions_per_day.png"), bbox_inches="tight"
        )

        drawBarChart(
            "Transactions per month",
            "EUR",
            eur_by_year_month.keys(),
            eur_by_year_month.values(),
        )
        plt.savefig(
            os.path.join(resultDir, "transactions_per_month.png"), bbox_inches="tight"
        )

        drawEurPerUser(
            "Transactions per user", "EUR", eur_by_user.keys(), eur_by_user.values()
        )
        plt.savefig(
            os.path.join(resultDir, "transactions_per_user.png"), bbox_inches="tight"
        )

        drawTimeSeries(
            "BTC wallet per day in last month",
            "BTC",
            wallet_balance_btc_by_day_keys_datetimes,
            wallet_balance_btc_by_day_values,
        )
        plt.savefig(
            os.path.join(resultDir, "wallet_balance_per_day.png"), bbox_inches="tight"
        )
