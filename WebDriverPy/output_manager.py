from datetime import datetime
from typing import Callable, Any, Self

from abc import ABC, abstractmethod

from .utils import saves_to_file, file_name_gen, resolve_resource_path


class OutputManager(ABC):
    """
    Responsible for printing and logging events and other messages.
    """

    @abstractmethod
    def print(self, content: str, level: str = "INFO") -> Self:
        """
        Prints the given content.
        :param content: The content to print.
        :param level: The log level.
        :return: The instance of OutputManager.
        """
        pass

    @abstractmethod
    def print_only(self, content: str, level: str = "INFO") -> Self:
        """
        Prints the given content and does not log it.
        :param content: The content to print.
        :param level: The log level.
        :return: The instance of OutputManager.
        """
        pass

    @abstractmethod
    def log(self, content: str, level: str = "INFO") -> Self:
        """
        Logs the given content.
        :param content: The content to log.
        :param level: The log level.
        :return: The instance of OutputManager.
        """
        pass

    @abstractmethod
    def plog(self, content: str, level: str = "INFO") -> Self:
        """
        Prints and logs the given content.
        :param content: The content to print and log.
        :param level: The log level.
        :return: The instance of OutputManager.
        """
        pass

    @abstractmethod
    def set_always_log_prints(self, value: bool) -> Self:
        """
        Set whether all print calls should also be logged.
        :param value: True to log prints, False otherwise.
        :return: The instance of OutputManager.
        """
        pass

    @abstractmethod
    def set_always_print_logs(self, value: bool) -> Self:
        """
        Set whether all logs should be printed.
        :param value: True to print logs, False otherwise
        :return: The instance of OutputManager
        """
        pass

    @abstractmethod
    def toggle_logs(self, value: bool) -> Self:
        """
        Toggle logging functionality.
        :param value: True to enable logging, False to disable.
        :return: The instance of OutputManager.
        """
        pass

    @abstractmethod
    def toggle_prints(self, value: bool) -> Self:
        """
        Toggle printing functionality.
        :param value: True to enable printing, False to disable.
        :return: The instance of OutputManager.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_default_logs_path() -> str:
        pass

    @staticmethod
    @abstractmethod
    def default_format_message(content: str, level: str) -> str:
        pass


class DefaultOutputManager(OutputManager):
    """
    The default implementation for the OutputManager

    The print function is the standard print() function

    The log function writes directly to a file called driver_logs_{i}.txt, where "{i}" may change
    to any number (starting from 2 if the original name is unavailable) such that the file name does not exist yet.

    The exact implementations can be changed by simply supplying a different one for the constructor.
    """

    def __init__(self,
                 print_func: Callable[[str, str], Any] = lambda content, level: print(DefaultOutputManager.default_format_message(content, level)),
                 log_func: Callable[[str, str], Any] = saves_to_file(
                     resolve_resource_path("./logs/driver_logs.txt"),
                     lambda content, level: f"{DefaultOutputManager.default_format_message(content, level)}\n"
                 ),
                 always_log_prints: bool = False,
                 print_logs: bool = False):
        self.__print_func = print_func
        self.__log_func = log_func
        self.__print_logs = print_logs
        self.__logs_prints = always_log_prints
        self.__prints_enabled = True
        self.__logs_enabled = True

        self.__update_methods()

    @staticmethod
    def get_default_logs_path() -> str:
        return resolve_resource_path("./logs/driver_logs.txt")

    @staticmethod
    def default_format_message(content: str, level: str) -> str:
        return f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} @ {level}]: {content}"

    def __print(self, content: str, level: str) -> Self:
        self.__print_func(content, level)
        return self
    __print_ref = __print

    def print(self, content: str, level: str = "INFO") -> Self:
        if self.__prints_enabled:
            self.__print(content, level)
        return self

    def print_only(self, content: str, level: str = "INFO") -> Self:
        if self.__prints_enabled:
            self.__print_func(content, level)
        return self

    def __log(self, content: str, level: str) -> Self:
        self.__log_func(content, level)
        return self
    __log_ref = __log

    def log(self, content: str, level: str = "INFO") -> Self:
        if self.__logs_enabled:
            self.__log(content, level)
        return self

    def plog(self, content: str, level: str = "INFO") -> Self:
        if self.__prints_enabled:
            self.__print_func(content, level)
        if self.__logs_enabled:
            self.__log_func(content, level)
        return self

    def set_always_log_prints(self, value: bool) -> Self:
        self.__logs_prints = value
        self.__update_methods()
        return self

    def set_always_print_logs(self, value: bool) -> Self:
        self.__print_logs = value
        self.__update_methods()
        return self

    def __update_methods(self) -> Self:
        self.__print = self.plog if self.__logs_prints else self.__print_ref
        self.__log = self.plog if self.__print_logs else self.__log_ref
        return self

    def toggle_logs(self, value: bool) -> Self:
        self.__logs_enabled = value
        return self

    def toggle_prints(self, value: bool) -> Self:
        self.__prints_enabled = value
        return self


class NoOutput(OutputManager):
    """
    OutputManager, which never produces any output.

    Only functionality (static methods):
        - Format messages using default_format_message()
        - Get default log path using get_default_logs_path()
    """

    def print(self, content: str, level: str = "INFO") -> Self:
        pass

    def print_only(self, content: str, level: str = "INFO") -> Self:
        pass

    def log(self, content: str, level: str = "INFO") -> Self:
        pass

    def plog(self, content: str, level: str = "INFO") -> Self:
        pass

    def set_always_log_prints(self, value: bool) -> Self:
        pass

    def set_always_print_logs(self, value: bool) -> Self:
        pass

    def toggle_logs(self, value: bool) -> Self:
        pass

    def toggle_prints(self, value: bool) -> Self:
        pass

    @staticmethod
    def get_default_logs_path() -> str:
        return resolve_resource_path("./logs/driver_logs.txt")

    @staticmethod
    def default_format_message(content: str, level: str) -> str:
        return f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} @ {level}]: {content}"
