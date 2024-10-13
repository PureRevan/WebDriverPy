import string
import json
import time
import subprocess

from datetime import timedelta, datetime
from itertools import cycle
from random import uniform, randint, choice
from threading import Thread
from os.path import join, abspath, basename, dirname, splitext
from typing import Callable, Self, Any, NoReturn
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError

import requests

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.window import WindowTypes

from .subpackages.PyProxies import load_proxies_list, RankedProxies, Proxy

from .output_manager import OutputManager, DefaultOutputManager, NoOutput

from .subpackages.PyProxies.proxy import ProtectedProxy
from .utils import (extract_from_zip, extract_all_from_zip, ensure_exists, check_file_exists, force_delete, read_content,
                    file_name_gen, find_files_with_extension, resolve_resource_path, is_authenticated_proxy_string, dump,
                    read_template_content)
from .exceptions import WindowRecorderException, DriverStillRunningException, DriverProxyException, DriverRequestsException


class WebDriver(webdriver.Chrome):
    """
    An extended and more accessible version of the selenium webdriver based on Chromium.

    It provides automatic binary downloads, support for proxies, a screen recorder, custom logs,
    automatic installation of an ad blocker and many other useful utilities.
    """

    def __init__(self,
                 chromedriver_path: str | None = None,
                 chrome_binary_path: str | None = None,
                 headless: bool = False,
                 no_cookies: bool = False,
                 start_maximized: bool = True,
                 allow_browser_recording: bool = True,
                 disable_dev_memory_restrictions: bool = True,
                 enable_safe_browsing: bool = True,
                 use_ad_blocker: bool = True,
                 disable_password_manager_popups: bool = True,
                 ignore_certificate_errors: bool = False,
                 output_manager: OutputManager | None = DefaultOutputManager(),
                 log_print_output: bool = False,
                 print_logs: bool = False,
                 disable_all_logs: bool = False,
                 disable_all_prints: bool = False,
                 download_directory: str = resolve_resource_path("./captures"),
                 recording_script_js: str = resolve_resource_path("./scripts/preciseMediaRecorder.js"),
                 prevent_fullscreen_js_script: str = resolve_resource_path("./scripts/preventFullScreen.js"),
                 recording_buffer_js: float = 0.05,
                 try_spoofing: bool = True,
                 avg_char_write_spoofing_delay: float = 0.2,
                 proxies: list[Proxy] | Proxy | list[str] | str | None = None,
                 proxy_auto_search_size: int = 50,
                 proxy_auto_rotation_size: int = 50,
                 late_init: bool = False,
                 clear_temp_dir: bool = True,
                 additional_driver_arguments: tuple[str, ...] = ("--disable-search-engine-choice-screen",),
                 **kwargs) -> None:
        """
        Configure the WebDriver here.

        Most Important Options:
        - no_cookies: Blocks cookies. (Some Websites need cookies to function (this needs to be False))
        - use_ad_blocker: Blocks ads by automatically installing uBlockOrigin in the browser.
        - start_maximized: Whether to start the browser with a maximized window.

        More Specific Important Options:
        - late_init: Whether to initialize the underlying Selenium Webdriver superclass later manually by calling the init() method
            This allows for configurations otherwise impossible while the driver is running before starting it, like clearing or managing internal directories / downloads
        - headless: Starts the browser in headless mode. (Experimental with some options)
        - try_spoofing: Whether the driver should use some basic anti-bot-detection measures, like typing like a
            human instead of just pasting the desired text into a textbox
        - proxies: Configure proxies settings

        Advanced Options:
        - additional_driver_arguments: Add any additional arguments for the Chromedriver
        - ignore_certificate_errors: Ignores certificate errors, such as invalid certificates
            (can be enabled together with using free (and unsecure) proxies)
        - disable_all_logs: Prevents the driver from creating a log file / using the log file

        :param chromedriver_path: The path to the Chromedriver binary. If set to None, the binary is automatically downloaded and saved.
        :param chrome_binary_path: The path to the Chrome binary. If set to None, the binary is automatically downloaded and saved.
        :param headless: Whether to use headless mode
        :param no_cookies: Whether to block all cookies.
            While True simplifies the process of scraping by blocking some popups, some websites may not function with this setting enabled
        :param start_maximized: Whether to start the window in maximized mode
        :param output_manager: The output manager instance to use for logging and other events. Use None for no output
        :param log_print_output: Whether to always log anything printed using the output_manager
        :param print_logs: Whether to print all logs
        :param disable_all_logs: Whether to disable all logs
        :param disable_all_logs: Whether to disable all prints
        :param allow_browser_recording: Whether to allow the browser to record the current tab
        :param disable_dev_memory_restrictions: Whether to disable certain memory restriction for chrome
        :param enable_safe_browsing: Whether to enable safe browsing
        :param use_ad_blocker: Whether to use an Ad blocker. If set to True, downloads (if necessary) and uses uBlock Origin
        :param download_directory: The download directory for chrome
        :param recording_script_js: The path to the javascript file used for recording the browser screen.
            By default, mediaRecorder.js and the improved preciseMediaRecorder.js are available in the scripts folder.
        :param prevent_fullscreen_js_script: The path to the javascript file used to prevent the fullscreen when calling .prevent_fullscreen()
        :param recording_buffer_js: The time buffer (in ms) by which to delay the end of the recording such
            that the final length is rather longer than too short.
            If the value is less than 1 it is interpreted as a ratio for the total duration. (e.g. 0.05 -> 5% longer)
        :param try_spoofing: Whether to attempt to look more like a normal browser and less like automated software by
            for instance changing user agent and passing some specific arguments to the Chromedriver
        :param avg_char_write_spoofing_delay: The average delay per character written by the send_keys() method of this class
        :param additional_driver_arguments: Any additional arguments directly supplied using the Options() class and .add_argument()
        :param disable_password_manager_popups: Whether to disable password manager popups
        :param proxies: Whether to use Proxies. Provide either a list of proxies to use as rotating proxies,
            None to use no proxies, a single proxy as a Proxy object or String, or "auto" to automatically load and test
            free proxies scraped from proxyscrape (not recommended).
            At "https://www.webshare.io/features/free-proxy" with an account one can get access to better proxies for free.
            To use proxies with authentication use the ProtectedProxy class.
            If free, scraped proxies are used nevertheless, SSL certificate errors such as
            "This website is not secure" may appear before one can access a page.
            To avoid this, the option ignore_certificate_errors is available but not recommended
        :param proxy_auto_search_size: Only takes effect when proxies is set to "auto": Defines how many free proxies
                should be gathered and tested. Is always at least proxy_auto_rotation_size
        :param proxy_auto_rotation_size: Only takes effect when proxies is set to "auto": Defines how many
                of the best found proxies should be used in the rotation pool.
        :param ignore_certificate_errors: Ignore any SSL certificate errors. (not recommended)
        :param late_init: Whether to initialize later. If set to True, initialization of the webdriver
            (webdriver.Chrome superclass) has to be done later manually via the init() method.
            Note that this simply delays the initialization of the superclass of the driver.
            The current status of initialization can be checked via the running attribute.
            The running attribute is set to false, when quit() is called or no initialization has happened yet,
                otherwise it is set to True.
            Be careful when using this class before it has been fully initialized!
        :param clear_temp_dir: Whether to clear the internal temporary directory at {package_dir}/temp
        :param kwargs: Any additional keyword arguments directly supplied to the webdriver.Chrome superclass


        Additional Note:
            Using headless mode may result in seeing a white blank screen, when using the automatically downloaded chrome for testing.
            There doesn't seem to be a direct solution to it (I at least couldn't find one) other than switching to a locally installed
            normal version of Chrome.

            The automatically installed Chrome flavour nevertheless remains "Chrome for Testing", even though this may cause the issue (?)
            The reason for this is, because it is pretty much the only easily portable and automatically
            installable Chrome version, which is also easy to match to any chromedriver in terms of versioning.
        """
        self._ensure_internal_base_dirs_exists()

        self.running = False
        self.output = output_manager if output_manager is not None else NoOutput()

        self.output.set_always_log_prints(log_print_output)
        self.output.set_always_print_logs(print_logs)
        self.output.toggle_logs(not disable_all_logs)
        self.output.toggle_prints(not disable_all_prints)

        temp_dir = resolve_resource_path("./temp")
        if clear_temp_dir:
            self.clear_temp_dir(temp_dir)
        ensure_exists(temp_dir)

        self.output.log("Starting driver...", "STARTUP")

        self._proxy_init_config(proxies, proxy_auto_rotation_size, proxy_auto_search_size)

        self._extensions = set()
        self.memory_restrictions_disabled = disable_dev_memory_restrictions
        self.allows_browser_recording = allow_browser_recording
        self.additional_driver_arguments = additional_driver_arguments
        self.is_headless = headless
        self.has_cookies = not no_cookies
        self.download_directory = download_directory
        self.try_spoofing = try_spoofing
        self.avg_char_write_spoofing_delay = avg_char_write_spoofing_delay

        self.recording_js_script = recording_script_js
        self.prevent_fullscreen_js_script = prevent_fullscreen_js_script

        self.recording_buffer_js = recording_buffer_js

        self.recording_resolution_js = (2560, 1440)
        self.fps_js_max = 165

        self.__reserved_file_names = []

        ensure_exists(self.download_directory)

        self.chromedriver_revision = None

        self.chromedriver_path = self.download_chromedriver_file(check_binary_versions=False) if chromedriver_path is None else abspath(chromedriver_path)

        self.chrome_binary = self.download_chrome_binary(check_binary_versions=False) if chrome_binary_path is None \
            else abspath(chrome_binary_path)

        self.check_binary_versions()

        chrome_options = Options()
        chrome_options.binary_location = self.chrome_binary

        self.output.log(f"Registered Chrome binary location: {self.chrome_binary}", "CONFIG")
        self.output.log(f"Registered Chromedriver.exe location: {self.chromedriver_path}", "CONFIG")

        prefs = {
            "download.default_directory": download_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": enable_safe_browsing,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_setting_values.popups": 0,
            "credentials_enable_service": not disable_password_manager_popups,
            "profile.password_manager_enabled": not disable_password_manager_popups
        }

        if no_cookies:
            prefs.update({"profile.default_content_setting_values.cookies": 2})

        chrome_options.add_experimental_option("prefs", prefs)

        self.proxy_extension: str | None = None

        if self.proxy_pool is not None:
            self.uses_proxy = True
            self._proxy_idx = 0
            self.proxy = self.proxy_pool[self._proxy_idx]

            self.output.log(f"Initial proxy configuration ({'protected' if self.uses_protected_proxy else 'unprotected'}): {self.proxy}", "CONFIG")

            if self.uses_protected_proxy:
                self.proxy_extension = self._configure_protected_proxy_extension()
                self._extensions.add(self.proxy_extension)
            else:
                chrome_options.add_argument(f"--proxy-server={self.proxy.protocol}://{self.proxy.ip}")
        else:
            self.uses_proxy = False
            self.output.log("No proxy configuration found...", "CONFIG")

        options = {
            "--disable-dev-shm-usage": disable_dev_memory_restrictions,
            "--headless=new": headless,
            "--start-maximized": start_maximized,
            "--use-fake-ui-for-media-stream": allow_browser_recording,
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36": try_spoofing,
            "--disable-blink-features=AutomationControlled": try_spoofing,
            "--disable-blink-features": try_spoofing,
            "--disable-notifications": True,
            "--disable-infobars": True,
            "--ignore_certificate_errors": ignore_certificate_errors
        }
        options.update({k: True for k in additional_driver_arguments})

        self.output.log(f"Registered Options: {options}", "CONFIG")
        self.output.log(f"Registered preferences: {prefs}", "CONFIG")

        additional_log_data = {
            "recording_buffer_js": recording_buffer_js,
            "recording_script_js": recording_script_js,
            "prints_logs": log_print_output,
            "output_manager": output_manager.__class__.__name__
        }

        self.output.log(f"Registered additional information: {additional_log_data}", "CONFIG")

        for option, is_enabled in options.items():
            if is_enabled:
                chrome_options.add_argument(option)

        if try_spoofing:
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

        if use_ad_blocker:
            ad_blocker_extension = self.download_ublock_origin()
            self._extensions.add(ad_blocker_extension)
            self.output.plog("Extension 'uBlock Origin' (ad blocker) successfully configured!")

        self.check_binary_versions()

        self._init_options = chrome_options
        self._init_kwargs = kwargs
        self._init_service = Service(executable_path=self.chromedriver_path)

        if not late_init:
            self.init()
        else:
            self.output.log("Driver initialization delayed to manual initialization!", "STARTUP")

    def init(self, **kwargs) -> Self:
        """
        :param kwargs: Any other keyword arguments relevant to the webdriver.Chrome class.
            Note that these values will be combined and overwrite overlapping values from the already passed kwargs of the __init__ method
        :return: Initializes the superclass webdriver.Chrome
        """
        self._init_kwargs.update(kwargs)

        if self._init_kwargs:
            self.output.log(f"Registered additional kwargs for superclass: {self._init_kwargs}", "CONFIG")

        extensions = ','.join(self._extensions)
        self._init_options.add_argument(f"--load-extension={extensions}")
        self.output.log(f"Registered extensions: {extensions}", "CONFIG")

        self.running = True
        super().__init__(service=self._init_service, options=self._init_options, **self._init_kwargs)

        self.output.log("Driver initialized!", "STARTUP")

        if self.try_spoofing:
            self.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return self


    def _proxy_init_config(self, proxies: list[Proxy] | Proxy | list[str] | str | None,
                           proxy_auto_rotation_size: int, proxy_auto_search_size: int) -> Self:
        if isinstance(proxies, list):
            self.output.log("Received proxy pool configuration...", "CONFIG")

            auth_proxies = [p for p in proxies if isinstance(p, ProtectedProxy) or
                            (isinstance(p, str) and is_authenticated_proxy_string(p))]
            rproxies = RankedProxies.from_trusted_protected(auth_proxies)
            rproxies.update_trusted_unprotected([p for p in proxies if p not in set(auth_proxies)])

            self.proxy_pool = rproxies.get_n_best(proxy_auto_rotation_size)
        elif isinstance(proxies, str):
            if proxies == "auto":
                self.output.log("Received automatic proxy configuration...", "CONFIG")

                proxy_auto_search_size = max(proxy_auto_search_size, proxy_auto_rotation_size)

                loaded = load_proxies_list(n=proxy_auto_search_size)

                if datetime.now() - loaded.data_from > timedelta(hours=12):
                    self.output.log("Found outdated proxies...", "CONFIG")
                    self.output.log("Fetching new proxies...", "CONFIG")
                    loaded = load_proxies_list(force_load=True, n=proxy_auto_search_size)
                else:
                    self.output.log(
                        f"Found cached proxies from "
                        f"{loaded.data_from.strftime(RankedProxies.saved_date_format)}...",
                        "CONFIG"
                    )

                self.proxy_pool = loaded.get_n_best(proxy_auto_rotation_size)
            else:
                self.output.log(f"Received single proxy configuration: {proxies}", "CONFIG")
                self.proxy_pool = (RankedProxies.from_trusted_protected([proxies]) if isinstance(proxies,
                                                                                                 str) and is_authenticated_proxy_string(
                    proxies)
                                   else RankedProxies.from_trusted_unprotected([proxies])).get_n_best(
                    proxy_auto_rotation_size)
        elif isinstance(proxies, Proxy):
            self.output.log(f"Received single proxy configuration: {proxies}", "CONFIG")
            self.proxy_pool = (RankedProxies.from_trusted_protected([proxies]) if isinstance(proxies, ProtectedProxy)
                               else RankedProxies.from_trusted_unprotected([proxies])).get_n_best(
                proxy_auto_rotation_size)
        elif proxies is not None:
            self.output.plog(f"Received invalid proxy configuration: {proxies}", "CONFIG-ERROR")

        if proxies is None or not self.proxy_pool:
            self.proxy_pool = None
        return self

    @property
    def uses_protected_proxy(self) -> bool:
        return isinstance(self.proxy, ProtectedProxy)

    def _configure_protected_proxy_extension(self, extension_location: str = resolve_resource_path("./extensions/proxy_auth")) -> str:
        if not self.uses_protected_proxy:
            raise DriverProxyException("ProtectedProxy was expected but non-protected one was selected as active proxy!")

        background_js_template = join(extension_location, "templates", "background.js")
        proxy_host, proxy_port = self.proxy.ip.rsplit(":", maxsplit=1)

        background_js_content = read_template_content(
            background_js_template,
            {
                "!__::HOST_TEMPLATE_DUMMY::__!": proxy_host,
                "!__::PORT_TEMPLATE_DUMMY::__!": proxy_port,
                "!__::SCHEME_TEMPLATE_DUMMY::__!": self.proxy.protocol,
                "!__::PASSWORD_TEMPLATE_DUMMY::__!": self.proxy.password,
                "!__::USERNAME_TEMPLATE_DUMMY::__!": self.proxy.username
            }
        )

        dump(background_js_content, join(extension_location, "background.js"), mode="w")
        return extension_location

    @staticmethod
    def _ensure_internal_base_dirs_exists() -> None:
        internal_dirs = [
            resolve_resource_path(rss)
            for rss in [
                "./captures",
                "./logs",
                "./chrome_binary",
                "./extensions/uBlockOrigin",
                "./extensions/proxy_auth",
                "./scripts",
                "./subpackages",
                "./temp"
            ]
        ]

        for internal_dir in internal_dirs:
            ensure_exists(internal_dir)

    def _refresh_proxy(self) -> str | None:
        self._proxy_idx = (self._proxy_idx + 1) % len(self.proxy_pool)
        self.proxy = self.proxy_pool[self._proxy_idx]

        proxy_extension = self._configure_protected_proxy_extension() if self.uses_protected_proxy else None

        self.output.log(f"New proxy configuration ({'protected' if self.uses_protected_proxy else 'unprotected'}): {self.proxy}", "CONFIG")

        return proxy_extension

    def rotate_proxy(self) -> Self:
        """
        :return: Rotates the current proxy. Note that this will quit and restart the driver!
        """
        if self.proxy_pool is None:
            raise DriverProxyException("Received no proxy configuration: Unable to rotate proxies!")
        self.quit()

        if self.proxy_extension is not None:
            # Remove old proxy extension
            self._extensions.remove(self.proxy_extension)

        self.proxy_extension = self._refresh_proxy()

        if self.proxy_extension is None:
            self._init_options.add_argument(f"--proxy-server={self.proxy.protocol}://{self.proxy.ip}")
        else:
            # Add new proxy extension
            self._extensions.add(self.proxy_extension)

        return self.init()

    def clear_downloads(self, chrome_binaries: bool = True, chromedriver: bool = True, temp_dir: bool = True, ad_blocker: bool = True) -> Self:
        self.output.log("Clearing downloads...", "CLEAR")
        if self.running:
            raise DriverStillRunningException("Unable to clear downloads: The driver is still running!")

        if chrome_binaries:
            self.clear_chrome_binaries()
        if chromedriver:
            self.clear_chromedriver_binaries()
        if temp_dir:
            self.clear_temp_dir()
        if ad_blocker:
            self.clear_ad_blocker_files()
        self.output.log("Successfully cleared downloads!")
        return self

    def clear_temp_dir(self, resolved_path: str = resolve_resource_path("./temp")) -> Self:
        if self.running:
            raise DriverStillRunningException("Unable to delete temporary directory: The driver is still running!")

        self.output.log(f"Clearing temporary directory {resolved_path}...", "CLEAR")
        force_delete(resolved_path, force_non_empty_dir_deletion=True)#
        self.output.log("Successfully cleared temporary directory!")
        return self

    def clear_logs(self, resolved_path: str = resolve_resource_path("./logs")) -> Self:
        self.output.log(f"Clearing logs directory {resolved_path}...", "CLEAR")
        force_delete(resolved_path, force_non_empty_dir_deletion=True)
        self.output.log("Successfully cleared logs directory!", "CLEAR")
        return self

    def get_binary_versions(self, silent: bool = False) -> tuple[str, str]:
        chromedriver_version = (subprocess.check_output([self.chromedriver_path, '--version'])
                                .decode('utf-8').strip()
                                .removeprefix("ChromeDriver").strip())
        chrome_version = splitext(basename(find_files_with_extension(dirname(self.chrome_binary), ".manifest")[0]))[0]

        if not silent:
            self.output.log(f"Found versions:\n\tChrome: {chrome_version}\n\tChromedriver: {chromedriver_version}")
        else:
            self.output.log(f"Found versions:\n\tChrome: {chrome_version}\n\tChromedriver: {chromedriver_version}")

        return chrome_version, chromedriver_version

    def check_binary_versions(self) -> Self:
        self.output.log("Checking binary versions...")
        chrome_ver, chromedriver_ver = self.get_binary_versions()

        chrome_ver = chrome_ver.split(".")[0].strip()
        chromedriver_ver = chromedriver_ver.split(".")[0].strip()

        if chrome_ver == chromedriver_ver:
            return
        elif chrome_ver > chromedriver_ver:
            self.output.plog("Incompatible version! Chromedriver outdated!")
            self.clear_chromedriver_binaries()
            self.download_chromedriver_file()
        else:
            self.output.plog("Incompatible version! Chrome binaries outdated!")
            self.clear_chrome_binaries()
            self.download_chrome_binary()
        return self

    def clear_chrome_binaries(self) -> Self:
        if self.running:
            raise DriverStillRunningException("Unable to delete binaries: The driver is still running!")

        self.output.plog("Clearing Chrome binaries", "CLEAR")
        force_delete(dirname(self.chrome_binary))
        self.output.plog("Cleared Chrome binaries!", "CLEAR")
        return self

    def clear_chromedriver_binaries(self) -> Self:
        if self.running:
            raise DriverStillRunningException("Unable to delete binaries: The driver is still running!")

        self.output.plog("Clearing chromedriver.exe...", "CLEAR")
        force_delete(self.chromedriver_path)
        self.output.plog("Cleared chromedriver.exe!", "CLEAR")
        return self

    def clear_ad_blocker_files(self, resolved_path: str = resolve_resource_path("./extensions/uBlockOrigin")) -> Self:
        if self.running:
            raise DriverStillRunningException("Unable to delete ad blocker files: The driver is still running!")

        self.output.plog(f"Clearing ad blocker files at {resolved_path}...", "CLEAR")
        force_delete(resolved_path)
        self.output.plog("Cleared ad blocker files!", "CLEAR")
        return self

    def quit(self) -> Self:
        super().quit()
        self.running = False
        self.output.log("Quit driver session!", "SHUTDOWN")
        return self

    def download_chromedriver_file(self, output_dir: str = resolve_resource_path("."),
                                   check_binary_versions: bool = True) -> str:
        if check_file_exists("chromedriver.exe", output_dir):
            self.output.print("Found and registered chromedriver.exe file...")
            return abspath(join(output_dir, "chromedriver.exe"))

        self.output.print("No downloaded chromedriver.exe found...")
        self.output.print("Starting download of chromedriver.exe...")
        try:
            response = json.loads(
                urlopen(
                    "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
                ).read()
            )

            stable_channels = response["channels"]["Stable"]
            self.chromedriver_revision = stable_channels.get("revision")

            download_url = [d for d in stable_channels["downloads"]["chromedriver"]
                            if d.get('platform') == 'win64'][0]["url"]
            urlretrieve(download_url, join(output_dir, 'chromedriver-win64.zip'))

            self.output.print("Downloaded Chromedriver...").print("Now extracting...")

            out = extract_from_zip(
                join(output_dir, "chromedriver-win64.zip"),
                "chromedriver.exe",
                output_dir,
                log_func=self.output.log
            )
            self.chromedriver_path = out

            if check_binary_versions:
                self.check_binary_versions()

            return out
        except URLError:
            self.output.print("Failed to download chromedriver.exe...")
            raise
        except KeyError:
            self.output.print("Failed to extract the download URL from the JSON response...")
            raise

    def get_chromedriver_version(self) -> str:
        self.output.print("Trying to fetch required revision number...")
        if self.chromedriver_revision is None:
            try:
                response = json.loads(
                    urlopen(
                        "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
                    ).read()
                )
                self.chromedriver_revision = response["channels"]["Stable"]["revision"]
            except URLError:
                self.output.print("Failed to fetch the required revision number...")
                raise
            except KeyError:
                self.output.print("Failed to extract the required revision number...")
                raise

        return self.chromedriver_revision

    def get_latest_chrome_binary_download(self) -> str:
        self.output.log("Fetching the latest available Chrome version info...")

        response = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        )

        response.raise_for_status()

        available_downloads = response.json()['channels']['Stable']["downloads"]["chrome"]
        win_download_url = [download["url"] for download in available_downloads if download.get("platform") == "win64"][0]

        return win_download_url

    def download_chrome_binary(self, output_dir: str = resolve_resource_path("."),
                               revision_number: int | None = None,
                               check_binary_versions: bool = True) -> str:
        chrome_binary_dir = join(output_dir, "chrome_binary")
        temp_dir = join(output_dir, "temp")

        ensure_exists(temp_dir)

        if check_file_exists("chrome.exe", chrome_binary_dir):
            self.output.print("Found and registered Chrome binary files...")
            return abspath(join(chrome_binary_dir, "chrome.exe"))

        self.output.print("No downloaded chrome binary found...")
        self.output.print("Starting download of Chrome binary...")
        version = revision_number if revision_number is not None else self.get_chromedriver_version()
        output_file = f"Win_{version}_chrome-win.zip"
        self.output.print(f"Detected required Chrome binary version {version}...")
        self.output.print_only("This may take some time...")
        self.output.print_only("Please wait until the download is finished and do not close this program...")

        tries = 3
        i = int(version)

        while tries > 0:
            try:
                urlretrieve(
                    f"https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/"
                    f"{output_file.replace('_', '%2F')}?alt=media",
                    join(temp_dir, output_file)
                )
                break
            except HTTPError as e:
                if e.code != 404:
                    raise e
                i -= 1
                tries -= 1

                self.output.plog(f"During Chrome binary download: Received 404 for version {version}", "WARNING")
                self.output.plog(f"Retrying with version {i} and {tries} tries left...")

                output_file = f"Win_{i}_chrome-win.zip"

        if tries < 1:
            self.output.plog(f"No tries left after trying version {i}!", "WARNING")
            self.output.plog(f"Retrying with the latest available version...")

            download_url = self.get_latest_chrome_binary_download()

            output_file = "chrome-win64.zip"

            try:
                urlretrieve(
                    download_url,
                    join(temp_dir, output_file)
                )
            except HTTPError:
                self.output.plog(f"Failed to download the latest version at URL {download_url}.", "ERROR")
                raise DriverRequestsException("Failed to download Chrome binary. Please check your network or the version availability.")

        out = abspath(
            join(
                extract_all_from_zip(
                    join(temp_dir, output_file),
                    output_dir=chrome_binary_dir,
                    log_func=self.output.log
                ),
                "chrome.exe"
            )
        )
        self.chrome_binary = out

        if check_binary_versions:
            self.check_binary_versions()

        return out

    def download_ublock_origin(self,
                               src: str = "https://api.github.com/repos/gorhill/uBlock/releases/latest",
                               force_fresh_download: bool = False) -> str:
        if check_file_exists("manifest.json", resolve_resource_path("./extensions/uBlockOrigin")) and not force_fresh_download:
            self.output.log("Found and registered uBlock Origin extension...")
            return resolve_resource_path("./extensions/uBlockOrigin")

        self.output.plog("Found no existing uBlock Origin extension: Downloading uBlock Origin...")

        response = requests.get(src)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.output.log(f"While fetching uBlock Origin (info): An HTTP error occurred: {str(e)}", "ERROR")
            raise DriverRequestsException(f"An HTTP error occurred: {str(e)}")

        release_info = response.json()

        crx_asset = None
        for asset in release_info["assets"]:
            if asset["name"].endswith(".chromium.zip"):
                crx_asset = asset
                break
        if not crx_asset:
            self.output.log("No CRX file found for uBlock Origin!", "ERRO")
            raise WebDriverException("CRX file for Chromium-based browsers not found in the latest release.")

        crx_url = crx_asset["browser_download_url"]
        self.output.log(f"Detected uBlock Origin download URL: {crx_url}...")
        crx_response = requests.get(crx_url)

        try:
            crx_response.raise_for_status()
        except requests.HTTPError as e:
            self.output.log(f"While fetching uBlock Origin (crx): An HTTP error occurred: {str(e)}", "ERROR")
            raise DriverRequestsException(f"An HTTP error occurred: {str(e)}")

        crx_file_path = resolve_resource_path("./extensions/uBlockOrigin/uBlock_latest.crx")
        with open(crx_file_path, "wb") as crx_file:
            crx_file.write(crx_response.content)

        self.output.plog("Download of uBlock Origin complete!")
        self.output.plog("Now extracting necessary extension files...")

        out = extract_all_from_zip(
            crx_file_path,
            output_dir=resolve_resource_path("./extensions/uBlockOrigin"),
            log_func=self.output.log
        )
        self.output.plog("Finished extracting extension files!")

        return out

    @staticmethod
    def __resolve_by(by: str) -> str:
        match by.lower():
            case "tag" | "tag_name" | "tag name":
                return By.TAG_NAME
            case "class" | "cls" | "class_name" | "class name":
                return By.CLASS_NAME
            case "css" | "selector" | "css_selector" | "css selector":
                return By.CSS_SELECTOR
            case _:
                return getattr(By, by.upper()) if hasattr(By, by.upper()) else by

    def find(self, value: str, by: str = "id") -> WebElement:
        self.output.log(f"Finding ({by} = {value})...")
        return self.find_element(by=self.__resolve_by(by), value=value)

    def find_all(self, value: str = None, by: str = "id") -> list[WebElement]:
        self.output.log(f"Finding all ({by} = {value})...")
        return self.find_elements(by=self.__resolve_by(by), value=value)

    def find_by_many(self, value_by_entries: dict[str, str] | tuple[dict[str, str], Callable[[WebElement], bool]]) -> list[WebElement]:
        if isinstance(value_by_entries, dict):
            items = list(value_by_entries.items())
            if not items:
                raise WebDriverException("Invalid arguments passed to find_by_many!")

            items, (first_value, first_by) = items[1:], items[0]

            left = self.find_all(first_value, first_by)

            for value, by in items:
                left = [element for element in left if element.get_attribute(by) == value]

            return left
        elif (isinstance(value_by_entries, tuple) and len(value_by_entries) > 1
              and isinstance(value_by_entries[0], dict) and callable(value_by_entries[1])):
            items, filter_func = value_by_entries
            items = list(items.items())
            if not items:
                raise WebDriverException("Invalid arguments passed to find_by_many!")

            items, (first_by, first_value) = items[1:], items[0]

            left = self.find_all(first_value, first_by)

            for by, value in items:
                left = [element for element in left if element.get_attribute(by) == value]

            filtered_elements = list(filter(filter_func, left))

            return filtered_elements
        else:
            raise WebDriverException("Invalid arguments passed to find_by_many!")

    def find_with_tag(self, tag: str, value: str, by: str = "id") -> WebElement:
        tag = tag.lower()

        self.output.log(f"Finding with tag {tag} ({by} = {value})...")

        return next(element for element in self.find_all(value, by) if element.tag_name.lower() == tag)

    def find_all_with_tag(self, tag: str, value: str, by: str = "id") -> list[WebElement]:
        tag = tag.lower()

        self.output.log(f"Finding all with tag {tag} ({by} = {value})...")

        return [element for element in self.find_all(value, by) if element.tag_name.lower() == tag]

    def wait(self, amount: float) -> Self:
        self.output.log(f"Waiting for {amount}s...")
        time.sleep(amount)
        return self

    def wait_until(self, condition: Callable[[Self | WebElement], bool | WebElement | list[WebElement]], timeout: float = 6,
                   reverse: bool = False) -> Self:
        if reverse:
            WebDriverWait(self, timeout).until_not(condition)
        else:
            WebDriverWait(self, timeout).until(condition)
        return self

    def wait_and_find(self, value: str, by: str = "id", timeout: float = 6) -> WebElement:
        self.wait_until_located(value, by, timeout)
        return self.find(value, by)

    def wait_and_find_all(self, value: str, by: str = "id", timeout: float = 6) -> list[WebElement]:
        self.output.log(f"Waiting and finding all ({by} = {value}) with timeout {timeout}...")
        return WebDriverWait(self, timeout).until(lambda *_: self.find_all(value, by))

    def wait_find_with_tag(self, tag: str, value: str, by: str = "id", timeout: float = 6) -> WebElement:
        self.wait_until_located(value, by, timeout)

        def _predicate(driver) -> WebElement:
            return driver.find_with_tag(tag, value, by)

        return WebDriverWait(self, timeout).until(_predicate)

    def wait_find_all_with_tag(self, tag: str, value: str, by: str = "id", timeout: float = 6) -> list[WebElement]:
        self.output.log(f"Waiting and finding all with tag {tag} ({by} = {value}) with timeout {timeout}...")

        def _predicate(driver) -> list[WebElement]:
            return driver.find_all_with_tag(tag, value, by)

        return WebDriverWait(self, timeout).until(_predicate)

    def wait_clickable_and_find(self, value: str, by: str = "id", timeout: float = 6) -> WebElement:
        self.wait_until_clickable(value, by, timeout)
        return self.find(value, by)

    def wait_until_located(self, value: str = None, by: str = "id", timeout: float = 6) -> Self:
        self.output.log(f"Waiting for PRESENCE ({by} = {value}) with timeout {timeout}...")
        self.wait_until(EC.presence_of_element_located((self.__resolve_by(by), value)), timeout=timeout)
        return self

    def wait_until_all_located(self, value: str = None, by: str = "id", timeout: float = 6) -> Self:
        self.output.log(f"Waiting for PRESENCE ({by} = {value}) with timeout {timeout}...")
        self.wait_until(EC.presence_of_all_elements_located((self.__resolve_by(by), value)), timeout=timeout)
        return self

    def wait_until_clickable(self, value: str = None, by: str = "id", timeout: float = 6) -> Self:
        self.output.log(f"Waiting for CLICKABLE ({by} = {value}) with timeout {timeout}...")
        self.wait_until(EC.element_to_be_clickable((self.__resolve_by(by), value)), timeout=timeout)
        return self

    def wait_for_user_input(self, message: str = "Press Enter to proceed...") -> Self:
        print()
        input(message)
        return self

    @staticmethod
    def get_user_input(message: str = "Press Enter to proceed...") -> str:
        print()
        return input(message)

    @staticmethod
    def verify_user_input(message: str, verification: Callable[[str], bool] = lambda m: bool(m.strip())) -> Any:
        print()
        answer = input(message)

        while not verification(answer):
            print("Invalid answer!")
            answer = input(message)

        return answer

    @property
    def body(self) -> WebElement:
        return self.find("body", "tag")

    def click(self, value: str = None, by: str = "id") -> Self:
        self.output.log(f"Clicking ({by} = {value})...")
        self.find(value, by).click()
        return self

    def click_js(self, value: str = None, by: str = "id") -> Self:
        self.output.log(f"Clicking using Javascript ({by} = {value})...")
        self.execute_script("arguments[0].click()", self.find(value, by))
        return self

    def send_keys(self, element: WebElement, text: str, may_miss_spoofing: bool = True) -> Self:
        avg_wait = self.avg_char_write_spoofing_delay * 2
        acc_factor = 1.5
        min_avg_wait = self.avg_char_write_spoofing_delay * 0.5

        chance_state = cycle([15, 5, 22])
        chance_to_mistype = next(chance_state)

        if self.try_spoofing:
            for char in text:
                if may_miss_spoofing and char in string.ascii_letters and randint(1, chance_to_mistype) == 1:
                    element.send_keys(choice(string.ascii_letters))
                    time.sleep(avg_wait * 0.8)
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(avg_wait / 2)

                    # Accelerate once
                    acc_factor = min(acc_factor + 0.125, 2.5)
                    chance_to_mistype = next(chance_state)

                element.send_keys(char)

                s_time = uniform(avg_wait / acc_factor, avg_wait * (3.25 - acc_factor))

                acc_factor = min(acc_factor + 0.125, 2.5)
                if s_time > self.avg_char_write_spoofing_delay:
                    avg_wait = max(avg_wait - s_time + self.avg_char_write_spoofing_delay, min_avg_wait)

                time.sleep(max(s_time, min_avg_wait))
        else:
            element.send_keys(text)
        return self

    def wait_click_write(self, text: str, value: str, by: str = "id", timeout: float = 6) -> WebElement:
        self.wait_clickable_and_find(value, by, timeout).click()
        self.send_keys(self.wait_clickable_and_find(value, by, timeout), text)
        if self.try_spoofing:
            time.sleep(uniform(0.15, 0.65))
        return self.wait_clickable_and_find(value, by, timeout)

    def wait_click_write_submit(self, text: str, value: str, by: str = "id",
                                submit_value: str | None = None, submit_by: str | None = None,  timeout: float = 6) -> Self:
        self.wait_click_write(text, value, by, timeout)
        if submit_value is not None:
            if submit_by is None:
                submit_by = "id"
            self.wait_and_submit_element(submit_value, submit_by, timeout)
        elif submit_by is None:
            self.wait_and_submit_element(value, by, timeout)
        return self

    def write_to(self, text: str, value: str, by: str = "id") -> WebElement:
        self.output.log(f"Writing '{text}' to ({by} = {value})...")
        self.send_keys(self.find(value, by), text)
        return self.find(value, by)

    def submit_element(self, value: str, by: str = "id") -> WebElement:
        self.output.log(f"Submitting ({by} = {value})...")
        self.find(value, by).submit()
        return self.find(value, by)

    def wait_and_click_js(self, value: str = None, by: str = "id", timeout: float = 6) -> Self:
        self.output.log(f"Waiting and clicking ({by} = {value}) with timeout {timeout}...")
        self.wait_until_clickable(value, by, timeout)
        self.click_js(value, by)
        return self

    def wait_and_click(self, value: str = None, by: str = "id", timeout: float = 6) -> Self:
        self.output.log(f"Waiting and clicking ({by} = {value}) with timeout {timeout}...")
        self.wait_until_clickable(value, by, timeout)
        self.click(value, by)
        return self

    def wait_and_write_to(self, text: str, value: str = None, by: str = "id", timeout: float = 6) -> WebElement:
        self.output.log(f"Waiting and writing '{text}' to ({by} = {value}) with timeout {timeout}...")
        self.wait_until_clickable(value, by, timeout)
        return self.write_to(text, value, by)

    def wait_and_submit_element(self, value: str = None, by: str = "id", timeout: float = 6) -> WebElement:
        self.output.log(f"Waiting and submitting ({by} = {value}) with timeout {timeout}...")
        self.wait_until_clickable(value, by, timeout)
        return self.submit_element(value, by)

    def close_tab(self) -> Self:
        self.close()
        return self

    def switch_to_tab(self, name: str) -> Self:
        self.switch_to.window(name)
        return self

    def open_new_tab(self) -> Self:
        self.output.log("Opening new Tab...")
        self.switch_to.new_window(WindowTypes.TAB)
        return self

    def open_new_window(self) -> Self:
        self.output.log("Opening new Window...")
        self.switch_to.new_window(WindowTypes.WINDOW)
        return self

    def fullscreen(self) -> Self:
        self.output.log("Attempting to activate fullscreen...")
        self.fullscreen_window()
        return self

    def prevent_fullscreen(self) -> Self:
        self.execute_script(read_content(self.prevent_fullscreen_js_script))
        return self

    def bring_to_foreground(self) -> Self:
        self.output.log("Bringing window to foreground...")
        self.switch_to.window(self.current_window_handle)
        return self

    @property
    def is_on_empty_tab(self) -> bool:
        return self.current_url.strip() in ["data:,", "about:blank"]

    def get_browser_size(self) -> tuple[int, int]:
        return self.execute_script("return [window.innerWidth, window.innerHeight];")

    def __capture_screen_js(self,
                            duration: float,
                            video_base_name: str,
                            fps: int) -> str:
        file_name = file_name_gen(video_base_name, do_not_use=self.__reserved_file_names)
        self.__reserved_file_names.append(file_name)

        width, height = self.recording_resolution_js

        recording_buffer = self.recording_buffer_js if self.recording_buffer_js > 1 \
            else str(int(duration * 1000 * self.recording_buffer_js))

        script = read_template_content(
            self.recording_js_script,
            {
                "!__::DURATION_TEMPLATE_DUMMY::__!": str(int(duration * 1000)),
                "!__::NAME_TEMPLATE_DUMMY::__!": basename(file_name),
                "!__::BUFFER_MS_TEMPLATE_DUMMY::__!": recording_buffer,
                "!__::FPS_IDEAL_TEMPLATE_DUMMY::__!": str(fps),
                "!__::FPS_MAX_TEMPLATE_DUMMY::__!": str(self.fps_js_max),
                "!__::RES_HEIGHT_TEMPLATE_DUMMY::__!": str(height),
                "!__::RES_WIDTH_TEMPLATE_DUMMY::__!": str(width)
            }
        )

        self.execute_script(script)
        time.sleep(duration)

        self.__reserved_file_names.remove(file_name)
        return file_name

    def capture_screen(self,
                       duration: float = 3,
                       output_path: str = resolve_resource_path("./captures"),
                       video_base_name: str = "webdriver_video.webm",
                       blocking: bool = True,
                       fps_if_available: int = 60,
                       capture_method: str | Callable[[float, str, int], str] = "Javascript") -> str | Thread:
        """
        Captures the screen of the browser and saves a video of the given duration to the given path with the given name

        Requires certain Webdriver settings that are set during initialization

        :param fps_if_available: The frames per second, if the capture method allows it.
        :param blocking: Whether the recording should block the execution of the current thread
        :param duration: The duration of the video in seconds
        :param output_path: The output path
        :param video_base_name: The base name of the video (if the name already exists, "_{i}" for the smallest
            available i (starting at 0) will be inserted before the file extension)
        :param capture_method: The method to capture the video.
            When set to "Javascript", Javascript code will be used to capture the current window and save the recording to the Downloads folder.
            It is recommended to use "Javascript".
            A custom function should take duration, the output path, the base file name and the fps as parameters and
             return the given path to the saved video file again.
        :return: The path to the saved video file if blocking is set to True, otherwise a Thread object
        """

        match capture_method.lower():
            case "javascript":
                self.output.log(f"Starting {duration}s {'blocking' if blocking else 'non-blocking'} screen capture: "
                                f"(capture_method = Javascript, video_name = {video_base_name}, fps = {fps_if_available},"
                                f" output_path = {output_path})...")
                target = self.__capture_screen_js
                args = (duration, video_base_name, fps_if_available)
            case _:
                if not callable(capture_method):
                    raise WindowRecorderException("Invalid capture method supplied!")

                self.output.log(f"Starting {duration}s {'blocking' if blocking else 'non-blocking'} screen capture: "
                                f"(fps = {fps_if_available}, capture_method = {capture_method}, video_name = {video_base_name}, "
                                f"output_path = {output_path})...")

                target = capture_method
                args = (duration, output_path, video_base_name, fps_if_available)

        if blocking:
            return target(*args)

        thread = Thread(target=target, args=args)
        thread.start()
        return thread

    def get_package_default_capture_path(self) -> str:
        return self.download_directory

    def get_driver_default_logs_path(self) -> str:
        return self.output.get_default_logs_path()

    @staticmethod
    def get_package_dir() -> str:
        return resolve_resource_path(".")

    @staticmethod
    def resolve_package_resource(resource: str) -> str:
        return resolve_resource_path(resource)

    def get(self, url: str) -> Self:
        super().get(url)
        return self

    def __raise_not_implemented(self, message: str) -> NoReturn:
        self.output.log(f"Encountered NotImplementedError:\n{message}", "ERROR")
        raise NotImplementedError(message)
