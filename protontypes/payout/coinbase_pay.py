#!/usr/bin/python3
from coinbase.wallet.client import Client
import os

api_key = os.environ['COINBASE_TOKEN']
api_secret = os.environ['COINBASE_SECRET']

from coinbase.wallet.client import Client

client = Client(api_key, api_secret)
account = client.get_primary_account()
tx = account.send_money(to='@protonmail.com', amount='0.00001', currency='BTC', skip_notifications='true')
print(tx)

