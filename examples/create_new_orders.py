from pyftx import FtxAPIException
from pyftx import Client as FtxClient
from loguru import logger
API = "your-api-key"
SECRET = "your-secret-key"
subaccount_name = "your-subaccount_name"

client = FtxClient(API, SECRET, subaccount=subaccount_name)


def create_new(iClient, symbol='FTT-PERP', side='buy', size=0.1, price=20, order_type='limit', reduceOnly=False, postOnly=False, ioc=False):
    try:
        ftx_order = iClient.place_order(
            market=symbol,
            side=side,
            price=price,
            size=size,
            type=order_type,
            ioc=ioc,
            reduceOnly=reduceOnly,
            postOnly=postOnly
        )
        print("ftx_order: ", ftx_order)
        return ftx_order
    except FtxAPIException as error:
        logger.error(error)
        return []


# -----
create_new(client)
