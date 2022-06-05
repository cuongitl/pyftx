import time
import aiohttp
import asyncio
import requests
from loguru import logger
from pyftx import FtxAPIException, FtxValueError, enums
from typing import Dict, Optional, Any
from requests import Request
import hmac
import urllib.parse

ENDPOINT_ORDERS = "/orders"
ENDPOINT_ORDERS_HISTORY = "{}/history".format(ENDPOINT_ORDERS)
ENDPOINT_ORDERS_CLIENTID = "{}/by_client_id".format(ENDPOINT_ORDERS)
ENDPOINT_ORDERS_TRIGGER = "/conditional_orders"
ENDPOINT_ORDERS_TRIGGER_HISTORY = "{}/history".format(ENDPOINT_ORDERS_TRIGGER)
ENDPOINT_WALLET = "/wallet"

HEADERS_KEY = "FTX-KEY"
HEADERS_SIGN = "FTX-SIGN"
HEADERS_TS = "FTX-TS"
HEADERS_SUBACCOUNT = "FTX-SUBACCOUNT"

HEADERS_KEY_US = "FTXUS-KEY"
HEADERS_SIGN_US = "FTXUS-SIGN"
HEADERS_TS_US = "FTXUS-TS"
HEADERS_SUBACCOUNT_US = "FTXUS-SUBACCOUNT"


class BaseClient:
    API_URL = "https://ftx.{}/api"

    def __init__(self, api: Optional[str] = None, secret: Optional[str] = None, tld: str = 'com'):
        self.API_KEY, self.API_SECRET = api, secret
        self.session = self._init_session()
        self.header = {}
        self.TIMEOUT = 45
        self.API_URL = self.API_URL.format(tld)

    def _get_header(self) -> Dict:
        header = {
            self.HEADERS_KEY: "",
            self.HEADERS_SIGN: "",
            self.HEADERS_TS: "",
        }
        if self.API_KEY:
            assert self.API_KEY
            header[self.HEADERS_KEY] = self.API_KEY
        return header

    def _init_session(self):
        raise NotImplementedError

    def _handle_response(self, response: requests.Response):
        code = response.status_code
        if code == 200:
            data = response.json()
            if not data['success']:
                logger.error("[ERROR] Request failed! {}".format(response.text))
                raise FtxAPIException(response.json(), code)
            return data['result']
        else:
            try:
                logger.error("[ERROR] Request failed! {}".format(response.text))
                raise FtxAPIException(response.json(), code)
            except ValueError:
                raise FtxValueError(response)


class Client(BaseClient):
    def __init__(self, api: Optional[str], secret: Optional[str], subaccount=None, tld: str = 'com'):
        self.subaccount = subaccount
        self.tld = tld
        self.HEADERS_KEY = HEADERS_KEY
        self.HEADERS_SIGN = HEADERS_SIGN
        self.HEADERS_TS = HEADERS_TS
        self.HEADERS_SUBACCOUNT = HEADERS_SUBACCOUNT
        if self.tld == "us":
            self.HEADERS_KEY = HEADERS_KEY_US
            self.HEADERS_SIGN = HEADERS_SIGN_US
            self.HEADERS_TS = HEADERS_TS_US
            self.HEADERS_SUBACCOUNT = HEADERS_SUBACCOUNT_US
        super().__init__(
            api=api,
            secret=secret,
            tld=tld
        )

    def _init_session(self) -> requests.Session:
        self.header = self._get_header()
        session = requests.session()
        session.headers.update(self.header)
        return session

    def _get(self, path: str, params=None):
        return self._request("get", path, params=params)

    def _post(self, path: str, params=None) -> Dict:
        return self._request("post", path, json=params)

    def _put(self, path: str, params=None) -> Dict:
        return self._request("put", path, json=params)

    def _delete(self, path: str, params=None) -> Dict:
        return self._request("delete", path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self.API_URL + path, **kwargs)
        self._sign_request(request)
        self.response = self.session.send(request.prepare())
        return self._handle_response(self.response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self.API_SECRET.encode(), signature_payload, 'sha256').hexdigest()
        request.headers[self.HEADERS_KEY] = self.API_KEY
        request.headers[self.HEADERS_SIGN] = signature
        request.headers[self.HEADERS_TS] = str(ts)
        if self.subaccount is not None:
            request.headers[self.HEADERS_SUBACCOUNT] = urllib.parse.quote(self.subaccount)

    """ Orders Zone"""

    def get_open_orders(self, **kwargs) -> Dict:
        return self._get(ENDPOINT_ORDERS, params=kwargs)

    def get_orders_history(self, **kwargs) -> Dict:
        return self._get(ENDPOINT_ORDERS_HISTORY, params=kwargs)

    def get_conditional_orders(self, **kwargs) -> Dict:
        return self._get(ENDPOINT_ORDERS_TRIGGER, params=kwargs)

    def get_conditional_orders_triggers(self, conditional_order_id) -> Dict:
        ftx_endpoint = f"{ENDPOINT_ORDERS_TRIGGER}/{conditional_order_id}/triggers"
        return self._get(ftx_endpoint)

    def get_conditional_order_history(self, **kwargs) -> Dict:
        return self._get(ENDPOINT_ORDERS_TRIGGER_HISTORY, params=kwargs)

    def place_order(self, **kwargs) -> Dict:
        try:
            return self._post(ENDPOINT_ORDERS, params=kwargs)
        except:
            time.sleep(0.2)
            return self._post(ENDPOINT_ORDERS, params=kwargs)

    def place_conditional_order(self, **kwargs) -> Dict:
        try:
            return self._post(ENDPOINT_ORDERS_TRIGGER, params=kwargs)
        except:
            time.sleep(0.2)
            return self._post(ENDPOINT_ORDERS_TRIGGER, params=kwargs)

    def modify_order(self, order_id, **kwargs) -> Dict:
        ftx_endpoint = f"{ENDPOINT_ORDERS}/{order_id}/modify"
        try:
            return self._post(ftx_endpoint, params=kwargs)
        except:
            time.sleep(0.2)
            return self._post(ftx_endpoint, params=kwargs)

    def modify_order_by_clientid(self, client_order_id, **kwargs) -> Dict:
        ftx_endpoint = f"{ENDPOINT_ORDERS}/by_client_id/{client_order_id}/modify"
        try:
            return self._post(ftx_endpoint, params=kwargs)
        except:
            time.sleep(0.2)
            return self._post(ftx_endpoint, params=kwargs)

    def modify_conditional_orders(self, order_id, **kwargs) -> Dict:
        ftx_endpoint = f"{ENDPOINT_ORDERS_TRIGGER}/{order_id}/modify"
        try:
            return self._post(ftx_endpoint, params=kwargs)
        except:
            time.sleep(0.2)
            return self._post(ftx_endpoint, params=kwargs)

    def get_order_status(self, order_id):
        return self._get(f"{ENDPOINT_ORDERS}/{order_id}")

    def get_order_status_by_clientid(self, client_order_id):
        return self._get(f"{ENDPOINT_ORDERS}/by_client_id/{client_order_id}")

    def cancel_order(self, order_id):
        ftx_endpoint = f"{ENDPOINT_ORDERS}/{order_id}"
        try:
            return self._delete(ftx_endpoint)
        except:
            time.sleep(0.2)
            return self._delete(ftx_endpoint)

    def cancel_order_by_clientid(self, client_order_id):
        ftx_endpoint = f"{ENDPOINT_ORDERS}/by_client_id/{client_order_id}"
        try:
            return self._delete(ftx_endpoint)
        except:
            time.sleep(0.2)
            return self._delete(ftx_endpoint)

    def cancel_conditional_orders(self, id):
        ftx_endpoint = f"{ENDPOINT_ORDERS_TRIGGER}/{id}"
        try:
            return self._delete(ftx_endpoint)
        except:
            time.sleep(0.2)
            return self._delete(ftx_endpoint)

    def cancel_orders(self, **kwargs):
        ftx_endpoint = f"{ENDPOINT_ORDERS}"
        try:
            return self._delete(ftx_endpoint, kwargs)
        except:
            time.sleep(0.2)
            return self._delete(ftx_endpoint, kwargs)

    def set_leverage(self, **kwargs):
        return self._post("/account/leverage", kwargs)

    def get_markets(self) -> Dict:
        return self._get("/markets")

    def get_klines(self, market: str, resolution: int, start_time=None, end_time=None) -> Dict:
        params = {"resolution": resolution}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time

        return self._get(f"/markets/{market}/candles", params=params)

    def get_account_info(self) -> Dict:
        return self._get("/account")

    def get_all_balances(self) -> Dict:
        return self._get("{}/all_balances".format(ENDPOINT_WALLET))

    def get_balances(self) -> Dict:
        return self._get("{}/balances".format(ENDPOINT_WALLET))

    def get_positions(self, **kwargs) -> Dict:
        return self._get("/positions", params=kwargs)

    def get_all_positions(self, **kwargs) -> Dict:
        return self._get("/all_positions", params=kwargs)

    def get_leverage_tokens(self) -> Dict:
        return self._get("/lt/tokens")

    def get_funding_payments(self) -> Dict:
        return self._get("/funding_payments")

    def get_funding_rate(self, **kwargs) -> Dict:
        return self._get("/funding_rates", params=kwargs)

    def get_all_subaccounts(self) -> Dict:
        return self._get("/subaccounts")

    def get_saved_addresses(self, **kwargs) -> Dict:
        return self._get("{}/saved_addresses".format(ENDPOINT_WALLET), params=kwargs)

    def get_deposit_history(self, **kwargs) -> Dict:
        return self._get("{}/deposits".format(ENDPOINT_WALLET), params=kwargs)

    def get_deposit_address(self, coin, **kwargs) -> Dict:
        ftx_endpoint = f"{ENDPOINT_WALLET}/deposit_address/{coin}"
        return self._get(ftx_endpoint, params=kwargs)

    def get_withdrawal_history(self, **kwargs) -> Dict:
        return self._get("{}/withdrawals".format(ENDPOINT_WALLET), params=kwargs)

    def request_withdrawal(self, **kwargs):
        return self._post("{}/withdrawals".format(ENDPOINT_WALLET), kwargs)


class AsyncClient(BaseClient):
    def __init__(
            self,
            api: Optional[str],
            secret: Optional[str],
            subaccount=None,
            tld: str = 'com',
            loop=None
    ):
        self.loop = loop or asyncio.get_event_loop()
        self.subaccount = subaccount
        self.tld = tld
        self.HEADERS_KEY = HEADERS_KEY
        self.HEADERS_SIGN = HEADERS_SIGN
        self.HEADERS_TS = HEADERS_TS
        self.HEADERS_SUBACCOUNT = HEADERS_SUBACCOUNT
        if self.tld == "us":
            self.HEADERS_KEY = HEADERS_KEY_US
            self.HEADERS_SIGN = HEADERS_SIGN_US
            self.HEADERS_TS = HEADERS_TS_US
            self.HEADERS_SUBACCOUNT = HEADERS_SUBACCOUNT_US
        super().__init__(
            api=api,
            secret=secret,
            tld=tld
        )

    @classmethod
    async def create(
            cls,
            api: Optional[str],
            secret: Optional[str],
            loop=None,
    ):
        self = cls(api, secret, loop)
        return self

    def _init_session(self) -> aiohttp.ClientSession:
        session = aiohttp.ClientSession(loop=self.loop, headers=self._get_header())
        return session

    async def close_connection(self):
        if self.session:
            assert self.session
            await self.session.close()

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self.API_URL + path, **kwargs)
        await self._sign_request(request)
        self.response = self.session.send(request.prepare())
        return await self._handle_response(self.response)

    async def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self.API_SECRET.encode(), signature_payload, 'sha256').hexdigest()
        request.headers[self.HEADERS_KEY] = self.API_KEY
        request.headers[self.HEADERS_SIGN] = signature
        request.headers[self.HEADERS_TS] = str(ts)
        if self.subaccount is not None:
            request.headers[self.HEADERS_SUBACCOUNT] = urllib.parse.quote(self.subaccount)

    async def _handle_response(self, response: requests.Response):
        code = response.status_code
        if code == 200:
            data = response.json()
            if not data['success']:
                logger.error("[ERROR] Request failed! {}".format(self.response.text))
                raise FtxAPIException(response.json(), code)
            return data['result']
        else:
            try:
                logger.error("[ERROR] Request failed! {}".format(self.response.text))
                raise FtxAPIException(response.json(), code)
            except ValueError:
                raise FtxValueError(response)

    async def _get(self, path: str, params=None):
        return await self._request("get", path, params=params)

    async def _post(self, path: str, params=None) -> Dict:
        return await self._request("post", path, json=params)

    async def _put(self, path: str, params=None) -> Dict:
        return await self._request("put", path, json=params)

    async def _delete(self, path: str, params=None) -> Dict:
        return await self._request("delete", path, json=params)

    async def get_available_symbol(self):
        return await self._get("public/info")
