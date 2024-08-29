from warnings import warn
from typing import Self, Callable, Iterable
from threading import Thread


class ThreadManager:
    def __init__(self, fill_target: Callable | None = None, fill_args: Iterable[Iterable] | None = None):
        self.threads = []

        if fill_target is not None:
            if fill_args is None:
                warn("[ThreadManager]: fill_args is None but fill_target is not None: Skipping thread execution.", UserWarning)
            self.fill(fill_target, fill_args)
        elif fill_args is not None:
            warn("[ThreadManager]: fill_target is None but fill_args is not None: Skipping thread execution.", UserWarning)

    def join(self) -> Self:
        for thread in self.threads:
            thread.join()
        return self

    def clear(self) -> Self:
        self.threads.clear()
        return self

    def fill(self, target: Callable, args: Iterable[Iterable]) -> Self:
        for thread_arguments in args:
            thread = Thread(target=target, args=thread_arguments)
            thread.start()

            self.threads.append(thread)

        return self

    def fill_join(self, target: Callable, args: Iterable[Iterable]) -> Self:
        return self.fill(target, args).join()
