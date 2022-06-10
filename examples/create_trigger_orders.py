from pyftx import FtxAPIException
from pyftx import Client as FtxClient
from loguru import logger
API = "your-api-key"
SECRET = "your-secret-key"
subaccount_name = "your-subaccount_name"
client = FtxClient(API, SECRET, subaccount=subaccount_name)

"""  trigger type: # "stop", "trailingStop", "takeProfit"; default is stop"""


def create_takeprofit(iClient, symbol='FTT-PERP', side='sell', size=0.1, orderPrice=35, triggerPrice=34, order_type='takeProfit', reduceOnly=True, postOnly=False, ioc=False):
    try:
        ftx_order = iClient.place_conditional_order(
            market=symbol,
            side=side,
            orderPrice=orderPrice,
            triggerPrice=triggerPrice,
            size=size,
            type=order_type,
            ioc=ioc,
            reduceOnly=reduceOnly,
            postOnly=postOnly
        )
        print("result: ", ftx_order)
        return ftx_order
    except FtxAPIException as error:
        logger.error(error)
        return []


def create_stoploss(iClient, symbol='FTT-PERP', side='buy', size=0.1, orderPrice=None, triggerPrice=35, order_type='stop', reduceOnly=True, postOnly=False, ioc=False):
    try:
        ftx_order = iClient.place_conditional_order(
            market=symbol,
            side=side,
            orderPrice=orderPrice,
            triggerPrice=triggerPrice,
            size=size,
            type=order_type,
            ioc=ioc,
            reduceOnly=reduceOnly,
            postOnly=postOnly
        )
        print("result: ", ftx_order)
        return ftx_order
    except FtxAPIException as error:
        logger.error(error)
        return []


# -----
create_takeprofit(client)
create_stoploss(client)


