from coinbase.wallet.client import Client
client = Client(<api_key>, <api_secret>)

address = client.get_address('2bbf394c-193b-5b2a-9155-3b4732659ede', 'dd3183eb-af1d-5f5d-a90d-cbff946435ff')
