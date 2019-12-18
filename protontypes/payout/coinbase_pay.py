#!/usr/bin/python3
from coinbase.wallet.client import Client
import os,json

coinbase_token = os.environ['COINBASE_TOKEN']
coinbase_secret = os.environ['COINBASE_SECRET']
client = Client(coinbase_token,coinbase_secret)
user = client.get_current_user()
user_as_json_string = json.dumps(user)
print(user_as_json_string)
