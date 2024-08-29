from selenium.common.exceptions import WebDriverException, TimeoutException
from requests import RequestException


class DriverException(WebDriverException):
    pass


class WindowRecorderException(DriverException):
    pass


class DriverStillRunningException(DriverException):
    pass


class DriverProxyException(DriverException):
    pass


class DriverRequestsException(DriverException, RequestException):
    pass


class DriverScriptException(WebDriverException):
    pass


class InvalidDriverConfiguration(DriverScriptException):
    pass
