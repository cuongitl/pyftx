# Python FTX API Sample Code

[FTX](https://ftx.com/referrals#a=121465957) is a cryptocurrency derivatives exchange.

You can find the FTX API docs [here](https://docs.ftx.com/#overview)


You can create API keys on your [profile page](https://ftx.com/profile).

This is is a wrapper around the FTX API as described on [FTX](https://docs.ftx.com/), including all features the API provides using clear and readable objects, both for the REST  as the websocket API's.

**If you think something is broken, something is missing or have any questions, please open an [Issue](https://gitlab.com/cuongitl/python-ftx-api/-/issues)**

* [Example FTX rest API](https://gitlab.com/cuongitl/python-ftx-api/-/blob/main/example_rest_api.py)

* [Example FTX websocket API](https://gitlab.com/cuongitl/python-ftx-api/-/blob/main/example_websocket_api.py)


## Sample Code 
> Change your API KEY and your SECRET KEY.
### Restful Api

```python
from pyftx import Client

API = "your-api-key"
SECRET = "your-secret-key"
subaccount_name = "your-subaccount_name"

client = Client(API, SECRET, subaccount=subaccount_name)
info = client.get_markets()
print(info)

```
### Websocket

```python
from pyftx import ThreadedWebsocketManager


def on_message(event, argument):
    msg = "{}.event: {}".format(argument, event)
    print("on message: ", msg)


def on_read(event):
    print(event)


API = "your-api-key"
SECRET = "your-secret-key"
subaccount_name = "your-subaccount_name"

wsm = ThreadedWebsocketManager(API, SECRET, subaccount=subaccount_name)
wsm.start()

# Un-auth subscribe - Public Channels
name = 'market_connection'
wsm.start_socket(on_read, socket_name=name)
wsm.subscribe(name, channel="ticker", op="subscribe", market="ETH-PERP")

# Auth subscribe - [filled](https://docs.ftx.com/#fills-2)
name = 'private_connection'
wsm.start_socket(on_read, socket_name=name)
wsm.login(socket_name=name)
wsm.subscribe(
    name,
    channel="fills",
    op="subscribe",
)

# Auth subscribe -[orders](https://docs.ftx.com/#orders-2)
ws_type = 'private_connection'
wsm.start_socket(on_read, socket_name=ws_type)
wsm.login(socket_name=ws_type)
wsm.subscribe(
    ws_type,
    channel="orders",
    op="subscribe",
)
```
### Websocket with arguments


```python
from functools import partial
# Un-auth subscribe - Public Channels
subaccount_name = "Cuongitl"
callback_with_arguments = partial(on_message, argument=subaccount_name)
name = 'market_connection'
wsm.start_socket(callback_with_arguments, socket_name=name)
wsm.subscribe(name, channel="ticker", op="subscribe", market="ETH-PERP")
```
## Donate / Sponsor
I develop and maintain this package on my own for free in my spare time. Donations are greatly appreciated. If you prefer to donate any other currency please contact me.

**BTC**:  `3LrqgdMbToh1mAD3sjhbv3oaEppXY7hkae`

**BTC**:  `0x329a9F2b01aDA25F15eAE4C633d3bed8442c7BC6`  (BSC)

**USDT**:  `0x329a9F2b01aDA25F15eAE4C633d3bed8442c7BC6`  (BSC)

**FTT**:  `0x329a9F2b01aDA25F15eAE4C633d3bed8442c7BC6`  (ERC-20)



