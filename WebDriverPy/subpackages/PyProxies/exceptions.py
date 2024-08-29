class ProxyException(Exception):
    pass


class InvalidProxyFetchingResponse(ProxyException):
    pass


class InvalidJSONResponse(InvalidProxyFetchingResponse):
    pass


class InvalidResponseFormat(InvalidProxyFetchingResponse):
    pass


class ProxyTestingException(ProxyException):
    pass


class InvalidSavedJSONFormat(ProxyException):
    pass

