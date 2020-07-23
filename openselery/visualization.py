import matplotlib.pyplot as plt
import numpy as np
import json
import datetime

def getOrUpdateDict(dict, key, defaultValue):
  if not key in dict:
    dict[key] = defaultValue

  return dict[key]

def groupBy(list, keyFun):
  dict = {}

  for elem in list:
    key = keyFun(elem)
    list = getOrUpdateDict(dict, key, [])
    list.append(elem)

  return dict

def transactionToYearMonthDay(transaction):
  creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
  return f'{creation_date.day}/{creation_date.month}/{creation_date.year}'

def transactionToYearMonth(transaction):
  creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
  return f'{creation_date.month}/{creation_date.year}'

def transactionToUserEmail(transaction):
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

# read transactions file
transactions_file = open(r'./result/transactions.txt').read()
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
plt.savefig("transactions_per_day.png")

drawBarChart("EUR transactions per month", "EUR", eur_by_year_month.keys(), eur_by_year_month.values())
plt.savefig("transactions_per_month.png")

drawBarChart("EUR transactions per user", "EUR", eur_by_user.keys(), eur_by_user.values())
plt.savefig("transactions_per_user.png")
