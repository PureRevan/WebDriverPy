from abc import ABC
from typing import Any

from .driver import WebDriver
from .exceptions import InvalidDriverConfiguration


class DriverScript(ABC):
    """
    Driver script abstract base class

    This can be used to implement a full driver script for any purpose, which can then easily be run at any point using the .run() method

    Any configuration and data may be put in the __init__() method or anywhere else

    Put the main content of the script in the run method
    On super().run(): Automatically opens a new tab if the current tab is not empty

    If the script requires specific configurations to function override check_driver_config and return a  String if
    the configuration is invalid explaining why it is invalid for the user.
    check_driver_config() should return None if there are no problems.
    It is automatically called when super().__init__() is called and raises the InvalidDriverConfiguration exception
    if the configuration is invalid
    """
    def __init__(self, driver: WebDriver):
        """
        :param driver: The webdriver to use
        """
        self.driver = driver

        invalid_config = self.check_driver_config()
        if invalid_config is not None:
            self.driver.output.log(f"Encountered invalid driver configuration: {invalid_config}", "SCRIPT-ERROR")
            raise InvalidDriverConfiguration(f"Encountered invalid driver config: {invalid_config}")

    def run(self) -> Any:
        """
        :return: Runs the script and may return a result depending on the script.
        """
        self.driver.output.log(f'Running script "{self.__class__.__name__}"', "SCRIPT")
        if not self.driver.is_on_empty_tab:
            self.driver.open_new_tab()

    def check_driver_config(self) -> None | str:
        """
        Checks the driver configuration
        :return: None if everything is fine and a String if the configuration is invalid explaining why it is invalid.
        """
        return None


class OpeningDriverScript(DriverScript):
    """
    A driver script beginning by opening a page
    """

    def __init__(self, driver: WebDriver, address: str):
        """
        :param driver: The Webdriver to be used
        :param address: The address to open on run()
        """
        super().__init__(driver)
        self.address = address

    def run(self) -> Any:
        super().run()
        self.driver.get(self.address)


class OpenGoogle(OpeningDriverScript):
    """
    Opens "google.com"

    Can act as a test script
    """

    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://google.com")

    def run(self) -> None:
        super().run()
        self.driver.wait_until_clickable("q", by="name")


class OpenWhatIsMyIP(OpeningDriverScript):
    """
    Opens "whatismyipaddress.com" to reveal ones IP address
    """

    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://whatismyipaddress.com")

    def run(self) -> None:
        super().run()


class GrabTempMail(OpeningDriverScript):
    """
    Grabs and returns a temporary email address from "https://temp-mail.org"
    """

    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://temp-mail.org")

    def run(self, open_new_tab_at_end: bool = True) -> str:
        super().run()

        mail = self.driver.wait_and_find("mail").text.strip()

        if open_new_tab_at_end:
            self.driver.open_new_tab()

        return mail

