from pyftx import FtxAPIException
from pyftx import Client as FtxClient
from loguru import logger

API = "your-api-key"
SECRET = "your-secret-key"
subaccount_name = "your-subaccount_name"
client = FtxClient(API, SECRET, subaccount=subaccount_name)


def cancel_order_id(iClient, orderId):
    try:
        ftx_order = iClient.cancel_order(
            order_id=orderId)
        print("result: ", ftx_order)
        return ftx_order
    except FtxAPIException as error:
        logger.error(error)
        return []


def cancel_orders(iClient, symbol=None, side=None, conditionalOrdersOnly=False, limitOrdersOnly=False):
    # Cancel all orders: if you're param, this will restrict to cancelling orders for that params!
    try:
        if symbol is not None and side is not None:
            result = iClient.cancel_orders(market=symbol, side=side,
                                           conditionalOrdersOnly=conditionalOrdersOnly, limitOrdersOnly=limitOrdersOnly)
        elif symbol is not None:
            result = iClient.cancel_orders(market=symbol,
                                           conditionalOrdersOnly=conditionalOrdersOnly, limitOrdersOnly=limitOrdersOnly)
        elif side is not None:
            result = iClient.cancel_orders(side=side,
                                           conditionalOrdersOnly=conditionalOrdersOnly, limitOrdersOnly=limitOrdersOnly)
        else:
            logger.warning("cancel all symbol.")
            result = client.cancel_orders()
        return result
    except FtxAPIException as error:
        logger.error(error)
        return []


# -----
# cancel an order by order id
cancel_order_id(client, orderId=214474937)
# -- cancel all orders
cancel_orders(client)
