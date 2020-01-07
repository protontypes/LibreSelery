from coinbase.wallet.client import Client

class CoinbaseConnector:
    def __init__(self,token,secret):
        self.client = Client(token,secret)

    def checkaddresses(tocheck):
        addresses = self.client.get_address(token,secret)
        for address in addresses:
            if address == tocheck:
                return true
        return false

    def payout(self,target_email,target_amount='0.00001'):
        account = self.client.get_primary_account()
        tx = account.send_money(to=target_email, amount=target_amount, currency='BTC', skip_notifications='true')
        return tx


if __name__ == "__main__":
    pass
