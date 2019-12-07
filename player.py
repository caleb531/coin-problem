#!/usr/bin/env python3

import pexpect


class Player(object):
    """Represents a generic Player program."""

    def __init__(self, path):
        self.path = path
        self.total_correct = 0
        self.total_incorrect = 0
        self.total_error = 0

    def start_program(self):
        self.program = pexpect.spawnu(self.path)
