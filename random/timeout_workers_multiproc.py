import multiprocessing
import time
import random
from functools import partial
from datetime import datetime
import typing as t
import math

import psutil
import pandas as pd


def i_might_fail_lol(i: int, df: pd.DataFrame) -> int:
    time.sleep(random.randint(0, 3))
    rows = df.shape[0]
    if random.random() > 0.9999:
        raise Exception
    return int(rows * i)


def main() -> None:
    df = pd.read_csv(
        "C:/Users/Evgenii/Downloads/sample.csv",
        header=None,
        delimiter="|",
        dtype="object"
    )
    print("Df shape:", df.shape)

    total_jobs = 200
    jobs = list(range(total_jobs))
    concurrent_limit = psutil.cpu_count()
    failed_jobs = []
    results = []
    futures: t.List[tuple] = []
    to_break = False
    timeout_sec = 3
    timeouts_allowed = 3
    time_out_records = {}
    with multiprocessing.Pool(processes=psutil.cpu_count()) as pool:
        while True:
            vacant = concurrent_limit - len(futures)
            for i in range(vacant):
                try:
                    job_i = jobs.pop(0)
                except IndexError:
                    to_break = True
                    break
                # Potential issue - time ticks from the moment you schedule
                # a task, but there're no guarantees the OS will start its
                # execution straight away!
                future = pool.apply_async(partial(i_might_fail_lol, job_i, df))
                time_started = datetime.now()
                futures.append((job_i, time_started, future))
                print("Launched a job indexed:", job_i)

            if len(futures):
                currently_running = len(futures)
                # Await a quarter of the oldest jobs
                for i in range(math.ceil(currently_running / 4)):
                    job_i, time_started, future = futures.pop(0)
                    elapsed = (datetime.now() - time_started).seconds
                    remaining_timeout = timeout_sec - elapsed
                    if remaining_timeout < 0:
                        remaining_timeout = 0
                    try:
                        result = future.get(timeout=remaining_timeout)
                        results.append(result)
                        print(f"Job {job_i} completed successfully")
                    # Catch workers that hung yet haven't failed
                    except multiprocessing.TimeoutError:
                        print(f"Job {job_i} timed out")
                        if (
                                job_i in time_out_records
                                and time_out_records[job_i] > timeouts_allowed
                        ):
                            failed_jobs.append(job_i)
                            print(
                                f"{job_i} failed after"
                                f" {time_out_records[job_i]} timeouts"
                            )
                        else:
                            if job_i not in time_out_records.keys():
                                time_out_records[job_i] = 1
                                jobs.append(job_i)
                            else:
                                jobs.append(job_i)
                                time_out_records[job_i] += 1
                                print(
                                    f"Job {job_i} rescheduled "
                                    f"{time_out_records[job_i]} time"
                                )
                            # A job got rescheduled, cant complete yet
                            if to_break:
                                to_break = False
                    except BaseException as e:
                        print(f"Job {job_i} failed entirely. Error: {e}")
                        failed_jobs.append(job_i)
            # No currently running jobs and no jobs to run left
            elif not len(futures) and to_break:
                break
            time.sleep(0.001)

        assert len(results) + len(failed_jobs) == total_jobs, "Wrong!"
        print("\n\nResults:", results)
        print("\nFailed jobs:", failed_jobs)
        print("\nTimeouts summary:", time_out_records)


if __name__ == "__main__":
    main()
