import datetime


class FPS:
    def __init__(self) -> None:
        self._start = None
        self._stop = None
        self._frames_processed = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self) -> None:
        self._stop = datetime.datetime.now()

    def update(self) -> None:
        self._frames_processed += 1

    def elapsed(self) -> int:
        return (self._stop - self._start).total_seconds()

    def get_fps(self) -> int:
        return int(self._frames_processed / self.elapsed())
