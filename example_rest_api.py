from pyftx import Client

API = "your-api-key"
SECRET = "your-secret-key"
subaccount_name = "your-subaccount_name"

client = Client(API, SECRET, subaccount=subaccount_name)
info = client.get_markets()
print(info)
