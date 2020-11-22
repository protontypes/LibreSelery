import json
from coinbase.wallet.client import Client
from libreselery import selery_utils


class CoinbaseConnector(selery_utils.Connector):
    def __init__(self, token, secret):
        super(CoinbaseConnector, self).__init__()
        self.client = Client(token, secret)
        self.account = self.client.get_primary_account()
        #self.addresses = self.account.get_addresses()

    def pastTransactions(self):
        return self.client.get_transactions(self.account.id)

    def iswalletAddress(self, tocheck):
        for wallet in self.addresses["data"]:
            if wallet["address"] == tocheck:
                return True
        return False

    def payout(
        self,
        target_email,
        target_amount,
        skip_notifications,
        description,
        cryptocurrency,
    ):
        tx = self.account.send_money(
            to=target_email,
            amount=float(target_amount),
            currency=cryptocurrency,
            skip_notifications=skip_notifications,
            description=description,
        )
        return tx

    def balancecheck(self):
        amount = self.account["balance"]["amount"]
        currency = self.account["balance"]["currency"]
        return amount, currency

    def native_balancecheck(self):
        native_amount = self.account["native_balance"]["amount"]
        native_currency = self.account["native_balance"]["currency"]
        return native_amount, native_currency

    def useremail(self):
        user = self.client.get_current_user()
        email = user["email"]
        return email
