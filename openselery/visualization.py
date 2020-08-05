import matplotlib.pyplot as plt
import numpy as np
import json
import datetime

from openselery.collection_utils import groupBy
from openselery.github_connector import GithubConnector

def transactionToYearMonthDay(transaction):
  creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
  return f'{creation_date.day}/{creation_date.month}/{creation_date.year}'

def transactionToYearMonth(transaction):
  creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
  return f'{creation_date.month}/{creation_date.year}'

def transactionToUserEmail(transaction):
  #user_name = GithubConnector.grabUserNameByEmail(transaction["to"]["email"])
  return transaction["to"]["email"]

def transactionIsLastMonth(transaction):
  now_date = datetime.datetime.now()
  creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
  diff_date = now_date - creation_date
  return diff_date.total_seconds() <= 30 * 24 * 60 * 60

def transactionIsEurSpent(transaction):
  return float(transaction["native_amount"]["amount"]) < 0 and transaction["native_amount"]["currency"] == "EUR"

def transactionToEur(transaction):
  assert transaction["native_amount"]["currency"] == "EUR"
  return float(transaction["native_amount"]["amount"])

def drawBarChart(title, xlabel, keys, values):
  _, diagram = plt.subplots()
  y_pos = np.arange(len(keys))
  diagram.barh(y_pos, values, align='center')
  diagram.set_yticks(y_pos)
  diagram.set_yticklabels(keys)
  diagram.invert_yaxis()  # labels read top-to-bottom
  diagram.set_xlabel(xlabel)
  diagram.set_title(title)

def visualizeTransactions(resultFolder):
  # read transactions file
  transactions_file = open(resultFolder + '/transactions.txt').read()
  transactions = json.loads(transactions_file)

  # prepare transaction data
  data_by_day_last_month = groupBy(filter(lambda t: transactionIsEurSpent(t) and transactionIsLastMonth(t), transactions["data"]), transactionToYearMonthDay)
  data_by_year_month = groupBy(filter(transactionIsEurSpent, transactions["data"]), transactionToYearMonth)
  data_by_user = groupBy(filter(transactionIsEurSpent, transactions["data"]), transactionToUserEmail)

  eur_by_day_last_month = { k: -1 * sum(map(transactionToEur, v)) for k,v in data_by_day_last_month.items() }
  eur_by_year_month = { k: -1 * sum(map(transactionToEur, v)) for k,v in data_by_year_month.items() }
  eur_by_user = { k: -1 * sum(map(transactionToEur, v)) for k,v in data_by_user.items() }

  # draw diagrams
  plt.rcdefaults()

  drawBarChart("EUR transactions per day in last month", "EUR", eur_by_day_last_month.keys(), eur_by_day_last_month.values())
  plt.savefig(resultFolder + "/transactions_per_day.png")

  drawBarChart("EUR transactions per month", "EUR", eur_by_year_month.keys(), eur_by_year_month.values())
  plt.savefig(resultFolder + "/transactions_per_month.png")

  drawBarChart("EUR transactions per user", "EUR", eur_by_user.keys(), eur_by_user.values())
  plt.savefig(resultFolder + "/transactions_per_user.png")


