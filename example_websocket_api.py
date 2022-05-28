from pyftx import ThreadedWebsocketManager
from functools import partial

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

# Auth subscribe -[orders](https://docs.ftx.com/#orders-2)
ws_type = 'private_connection'
wsm.start_socket(on_read, socket_name=ws_type)
wsm.login(socket_name=ws_type)
wsm.subscribe(
    ws_type,
    channel="orders",
    op="subscribe",
)

# Auth subscribe - [filled](https://docs.ftx.com/#fills-2)
name = 'private_connection'
wsm.start_socket(on_read, socket_name=name)
wsm.login(socket_name=name)  # already login above, you can disable this line.
wsm.subscribe(
    name,
    channel="fills",
    op="subscribe",
)

# ### Websocket with arguments
# Un-auth subscribe - Public Channels
subaccount_name = "Cuongitl"
callback_with_arguments = partial(on_message, argument=subaccount_name)
name = 'market_connection'
wsm.start_socket(callback=callback_with_arguments, socket_name=name)
wsm.subscribe(name, channel="ticker", op="subscribe", market="ETH-PERP")
