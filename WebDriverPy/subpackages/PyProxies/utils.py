from typing import Callable
from functools import wraps
from timeit import default_timer
from os.path import exists, dirname, join
from os import makedirs
import random
import json

import requests

from .exceptions import ProxyTestingException
from .test_urls import test_urls as urls_to_test
from .thread_manager import ThreadManager


def resolve_resource_path(resource_name: str,
                          add_data_dir: str = "data",
                          ensure_exists: bool = True) -> str:
    resource_path = join(dirname(__file__), add_data_dir, resource_name)

    if ensure_exists:
        makedirs(dirname(resource_path), exist_ok=True)

    return str(resource_path)


def timed_print(f: Callable):
    """
    :param f: Callable to be timed
    :return: Returns a wrapper around f printing the time it took to execute f
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = default_timer()
        _res = f(*args, **kwargs)
        print(f"{f.__name__} took {default_timer() - start}s")
        return _res

    return wrapper


def timed(f: Callable) -> Callable:
    """
    :param f: Callable to be timed
    :return: Returns a wrapper around f returning the time it took to execute f as the first return value
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = default_timer()
        _res = f(*args, **kwargs)
        return default_timer() - start, _res

    return wrapper


def ignores_timeout(f: Callable) -> Callable:

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.Timeout:
            pass

    return wrapper


def ignores_request_exception(f: Callable) -> Callable:

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            pass

    return wrapper


def pick_random(test_urls: dict[str, float]) -> tuple[str, float]:
    key = random.choice(list(test_urls.keys()))
    return key, test_urls[key]


def test_proxy(test_url: str, test_url_time: float, proxy: str, proxy_protocol: str, test_num: int = 3):
    time_list = []

    try:
        @ignores_request_exception
        def speed_test():
            time_list.append(timed(lambda: requests.get(test_url, proxies={proxy_protocol: proxy}, timeout=8))()[0])

        ThreadManager(speed_test, [()] * test_num).join()

        return (sum(time_list) / test_num) - test_url_time
    except requests.exceptions.RequestException as e:
        raise ProxyTestingException(str(e))


def generate_test_urls() -> dict[str, float]:
    time_dict = {}

    def test_url_task(test_url: str):
        time_dict.update({test_url: test_url_speed(test_url)})

    ThreadManager(test_url_task, [(url,) for url in urls_to_test]).join()

    return time_dict


def test_url_speed(url: str, test_num: int = 3) -> float:
    time_list = []

    @ignores_request_exception
    def speed_test() -> None:
        time_list.append(timed(lambda: requests.get(url, timeout=8))()[0])

    ThreadManager(speed_test, [()] * test_num).join()

    return sum(time_list) / test_num


def load_test_urls(save_path: str = resolve_resource_path("test_urls_save.json"), saves: bool = True) -> dict[str, float]:
    if exists(save_path):
        with open(save_path, "r") as file:
            content = json.load(file)
    else:
        content = generate_test_urls()
        if saves:
            save_test_urls(content, save_path=save_path)

    return {k: v for k, v in content.items() if v < 5.0}


def save_test_urls(test_urls: dict[str, float], save_path: str = resolve_resource_path("test_urls_save.json")):
    if not exists(save_path):
        open(save_path, "x").close()

    with open(save_path, "w") as file:
        json.dump(test_urls, file)


def load_request_args(alt_headers: dict[str, str], alt_params: dict[str, str], ssl_support_required: bool = True) -> tuple[dict[str, str], dict[str, str]]:
    params = {
        'request': 'displayproxies',
        'protocol': 'socks5',
        'ssl': 'yes' if ssl_support_required else 'all',
        'anonymity': 'elite',
        'timeout': '10000',
        'proxy_format': 'ipport',
        'format': 'json',
    } if alt_params is None else alt_params

    headers = {
        'authority': 'api.proxyscrape.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'de-DE,de;q=0.9',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Opera GX";v="106"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    } if alt_headers is None else alt_headers

    return params, headers




