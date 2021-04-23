import random
import threading
import time
from queue import Queue
from typing import *


"""
Try downloading your dfs this way? Might help. Try async for f sake
"""


def timer(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        t1 = time.perf_counter()
        result = func(*args, **kwargs)
        print("Execution time:", time.perf_counter() - t1)
        return result

    return wrapper


def download_dataframe(df_lenght):
    print("Downloading df of size:", df_lenght)
    time.sleep(random.randint(0, 10))
    return [random.randint(0, 100) for _ in range(df_lenght)]


def run_in_background(func: Callable, *args, **kwargs):
    q = Queue(maxsize=1)
    t = threading.Thread(target=lambda: q.put(func(*args, **kwargs)), daemon=True)
    t.start()
    return q


@timer
def main():
    df1 = run_in_background(download_dataframe, 5)
    df2 = run_in_background(download_dataframe, 6)
    df3 = run_in_background(download_dataframe, 7)
    df4 = run_in_background(download_dataframe, 8)
    df5 = run_in_background(download_dataframe, 9)
    for df in [df1, df2, df3, df4, df5]:
        print("Got df:", df.get())


if __name__ == "__main__":
    main()
