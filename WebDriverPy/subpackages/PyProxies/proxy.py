import json
from dataclasses import dataclass
from datetime import datetime
from os import remove
from os.path import exists
from typing import Self

from .utils import load_test_urls, test_proxy, pick_random, resolve_resource_path
from .exceptions import InvalidSavedJSONFormat, ProxyTestingException


@dataclass
class Proxy:
    ip: str
    protocol: str


@dataclass
class FetchedProxy(Proxy):
    ip: str
    protocol: str
    average_timeout: float


@dataclass
class ProtectedProxy(Proxy):
    ip: str
    protocol: str
    username: str
    password: str

    @staticmethod
    def extract_proxy_string_components(entire_proxy_string: str) -> tuple[str, str, str, str]:
        protocol, rest = entire_proxy_string.split("://", maxsplit=1) if "://" in entire_proxy_string else "http", entire_proxy_string
        ip, port, user, password = rest.split(":")

        return f"{ip}:{port}", protocol, user, password

    @classmethod
    def from_string(cls, proxy_string: str) -> Self:
        return cls(*cls.extract_proxy_string_components(proxy_string))


class RankedProxies:
    saved_date_format = "%d.%m.%Y, %H:%M:%S"

    def __init__(self, proxies: list[Proxy] = None, test_num: int = 5,
                 alt_data: list[tuple[Proxy, float]] = None, saves: bool = True):
        self.proxies: list[tuple[Proxy, float]] = sorted([
            (proxy, proxy_time) for proxy in proxies
            if (proxy_time := self.check_proxy(proxy, test_num=test_num)) is not None
        ], key=lambda s: s[1]) if alt_data is None else alt_data

        self.data_from = datetime.now()

        if saves:
            self.save()

    @property
    def count(self):
        return len(self.proxies)

    def update(self, proxies: list[Proxy] = None, test_num: int = 3):
        self.proxies: list[tuple[Proxy, float]] = sorted([
            (proxy, proxy_time) for proxy in proxies
            if (proxy_time := self.check_proxy(proxy, test_num=test_num)) is not None
        ] + self.proxies, key=lambda s: s[1])

    def get_best(self) -> Proxy:
        return self.proxies[0][0]

    def get_n_best(self, n: int) -> list[Proxy]:
        return [proxy[0] for proxy in self.proxies[:n]]

    def save(self, path: str = resolve_resource_path("saved_free_proxies.json")):
        if not exists(path):
            open(path, "x").close()

        with open(path, "w") as file:
            json.dump({
                "type": "RankedProxies",
                "proxies": [((proxy[0].ip, proxy[0].protocol), proxy[1]) for proxy in self.proxies],
                "date": self.data_from.strftime(RankedProxies.saved_date_format)
                }, file)

    def clear(self, deletes_file: bool = True, path: str = resolve_resource_path("saved_free_proxies.json")):
        self.proxies.clear()
        if deletes_file:
            remove(path)

    def update_trusted_unprotected(self, proxies: list[Proxy] | list[str]):
        self.proxies = sorted(
            self.proxies + RankedProxies.__normalize_unprotected_proxy_list(proxies),
            key=lambda s: s[1]
        )

    def update_trusted_protected(self, proxies: list[Proxy] | list[str]):
        self.proxies = sorted(
            self.proxies + RankedProxies.__normalize_protected_proxy_list(proxies),
            key=lambda s: s[1]
        )

    @staticmethod
    def __normalize_unprotected_proxy_list(proxies: list[Proxy] | list[str]):
        return [(proxy if isinstance(proxy, Proxy) else Proxy(*tuple(reversed(proxy.split("://", maxsplit=1)))), float(-10e12 + i)) for i, proxy in enumerate(proxies)]

    @staticmethod
    def __normalize_protected_proxy_list(proxies: list[Proxy] | list[str]):
        return [(proxy if isinstance(proxy, ProtectedProxy) else ProtectedProxy(*ProtectedProxy.extract_proxy_string_components(proxy)), float(-10e12 + i))
                      for i, proxy in enumerate(proxies)]

    @classmethod
    def from_trusted_unprotected(cls, proxies: list[Proxy] | list[str]):
        """
        :param proxies: The list of trusted proxies as either Proxy objects or strings like "{protocl}://{ip}:{port}"
            like "https://127.0.0.1:8080" (not an actual proxy).
            Do not pass proxies in authentication in here! Use the from_trusted_protected() method for that instead!
        :return: An instance of RankedProxies, where the trusted proxies will be considered best. The proxies first in the list will be prioritized, when calling get_best() or get_best_n()
        """
        if not proxies:
            return RankedProxies(alt_data=[], saves=False)
        return RankedProxies(
            alt_data=RankedProxies.__normalize_unprotected_proxy_list(proxies),
            saves=False
        )

    @classmethod
    def from_trusted_protected(cls, proxies: list[ProtectedProxy] | list[str]):
        """
        :param proxies: The list of trusted proxies as either Proxy objects or strings like "{protocl}://{ip}:{port}:{user}:{password}"
            like "https://127.0.0.1:8080:testUser:testPassword" (not an actual proxy)
        :return: An instance of RankedProxies, where the trusted proxies will be considered best. The proxies first in the list will be prioritized, when calling get_best() or get_best_n()
        """
        if not proxies:
            return RankedProxies(alt_data=[], saves=False)
        return RankedProxies(
            alt_data=RankedProxies.__normalize_protected_proxy_list(proxies),
            saves=False
        )

    @classmethod
    def load(cls, path: str = resolve_resource_path("saved_free_proxies.json")):
        with open(path, "r") as file:
            content = json.load(file)

            try:
                rkp = RankedProxies(alt_data=[(Proxy(proxy[0][0], proxy[0][1]), proxy[1])
                                              for proxy in content["proxies"]], saves=False)
            except KeyError:
                raise InvalidSavedJSONFormat("Data at the saved file location is invalid.")

        data_from: str = content.get("date")
        if data_from is not None:
            rkp.data_from = datetime.strptime(data_from, RankedProxies.saved_date_format)

        return rkp

    @staticmethod
    def check_proxy(proxy: Proxy, test_num: int = 3) -> float | None:
        if test_num < 1:
            return 0

        test_urls = load_test_urls()

        try:
            return test_proxy(*pick_random(test_urls), proxy=proxy.ip, proxy_protocol=proxy.protocol, test_num=test_num)
        except ProxyTestingException:
            return None

