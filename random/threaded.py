import functools
import threading
import time
import typing as t
from concurrent.futures import Future
from traceback import format_exc


class threaded:
    def __init__(self, name: t.Optional[str] = None, daemon: bool = True) -> None:
        threaded._validate_args(name, daemon)
        self._name = name
        self._daemon = daemon

    def __call__(self, func: t.Callable) -> t.Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Future:
            future = Future()
            self._start_thread(
                lambda: threaded._resolve_future(func, future, *args, **kwargs)
            )
            return future

        return wrapper

    @staticmethod
    def _validate_args(name: t.Optional[str], daemon: bool) -> None:
        if name is not None and not isinstance(name, str):
            raise TypeError("Name is to be either None or a string")
        if daemon is not None and not isinstance(daemon, bool):
            raise TypeError("Daemon is to be either None or a bool")

    def _start_thread(self, func: t.Callable) -> threading.Thread:
        thread = threading.Thread(target=func, name=self._name)
        thread.daemon = self._daemon
        thread.start()
        return thread

    @staticmethod
    def _resolve_future(func: t.Callable, future: Future, *args, **kwargs) -> None:
        """Gets run in another thread. Future is the shared object"""
        future.set_running_or_notify_cancel()
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            e.traceback = format_exc()
            future.set_exception(e)
        else:
            future.set_result(result)


@threaded()
def download_a_file(filename: str) -> str:
    print("Downloading file:", filename)
    time.sleep(3)
    return f"Filename {filename} downloaded"


def main() -> int:
    f1 = download_a_file("1.png")
    f2 = download_a_file("2.png")
    f3 = download_a_file("3.png")
    for future in (f1, f2, f3):
        print(future.result())

    return 0


if __name__ == "__main__":
    s = time.perf_counter()
    main()
    print(f"Main took: {time.perf_counter() - s: .4f} seconds")
