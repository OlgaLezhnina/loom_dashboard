from contextlib import contextmanager
import time


class Timer:
    def __init__(self, name="timer"):
        self.name = name
        self.time = 0.0
        self._start_time = None

    def start(self):
        self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time is None:
            return
        self.time += time.perf_counter() - self._start_time
        self._start_time = None

    def report(self):
        print(f"{self.name} took {self.time} seconds")

    def reset(self):
        self.time = 0.0
        self._start_time = None


@contextmanager
def timing(timer=None):
    instant_report = False
    if timer is None:
        timer = Timer()
        instant_report = True
    if isinstance(timer, str):
        timer = Timer(timer)
        instant_report = True
    try:
        timer.start()
        yield timer
    finally:
        timer.stop()
        if instant_report:
            timer.report()
