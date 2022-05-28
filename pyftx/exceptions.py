class FtxAPIException(Exception):
    def __init__(self, resp_json, status_code):
        self.code = status_code
        self.message = resp_json['error']

    def __str__(self):
        return 'APIError(code=%s): %s' % (self.code, self.message)


class FtxValueError(Exception):
    def __init__(self, response) -> None:
        self.response = response

    def __str__(self):
        return f"Invalid Response: {self.response.text}"


class FtxWebsocketUnableToConnect(Exception):
    pass
