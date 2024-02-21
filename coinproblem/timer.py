#!/usr/bin/env python3

# https://stackoverflow.com/a/22348885/560642

import signal


class TimeoutError(Exception):
    pass


class Timer:

    def __init__(self, seconds=1, error_message="TimeoutError"):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)
