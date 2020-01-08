from coinbase.wallet.client import Client
import json

class CoinbaseConnector:
    def __init__(self,token,secret):
        self.client = Client(token,secret)
        self.account = self.client.get_primary_account()
        self.addresses = self.account.get_addresses()

    def checkaddress(self,tocheck):
        for address in tocheck:
            if self.addresses['data'][0]['address'] == tocheck:
                return True
        return False

    def payout(self,target_email,target_amount='0.00001'):
        account = self.client.get_primary_account()
        tx = account.send_money(to=target_email, amount=target_amount, currency='BTC', skip_notifications='true')
        return tx

if __name__ == "__main__":
    pass
