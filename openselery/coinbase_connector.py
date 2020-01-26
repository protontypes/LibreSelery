import json
from coinbase.wallet.client import Client
from openselery import selery_utils

class CoinbaseConnector(selery_utils.Connector):
    def __init__(self, token, secret):
        super(CoinbaseConnector, self).__init__()
        self.client = Client(token, secret)
        self.account = self.client.get_primary_account()
        self.addresses = self.account.get_addresses()

    def pastTransactions(self):
        return self.client.get_transactions(self.account.id)

    def isWalletAddress(self, tocheck):
        for address in tocheck:
            if self.addresses['data'][0]['address'] == tocheck:
                return True
        return False

    def payout(self, target_email, target_amount, skip_notifications, description):
        tx = self.account.send_money(
            to=target_email, amount=float(target_amount), currency='BTC', skip_notification=['false','true'][skip_notifications], description=description)
        return tx
