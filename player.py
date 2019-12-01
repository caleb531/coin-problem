#!/usr/bin/env python3

import pexpect


class Player(object):
    """Represents a generic Player program."""

    def __init__(self, program_path):
        self.program = pexpect.spawnu(program_path)
        self.total_correct = 0
        self.total_incorrect = 0
        self.total_error = 0
