#!/usr/bin/env python3

import argparse
import json
import random

import pexpect

from player import Player


i = 0
# Constants
PENNY_VALUE = 0.01
NICKEL_VALUE = 0.05
DIME_VALUE = 0.1
QUARTER_VALUE = 0.25


# Parse command-line arguments passed to referee player
def parse_cli_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'players',
        metavar='player',
        nargs='+',
        type=Player,
        help='one or more player programs to execute')
    parser.add_argument(
        '--timeout',
        '-t',
        type=int,
        default=3,
        help='the number of seconds each player will run before timing out')
    parser.add_argument(
        '--min-count',
        '--min',
        metavar='--min',
        type=int,
        default=1,
        help='the minimum number of coins per coin type to be generated')
    parser.add_argument(
        '--max-count',
        '--max',
        metavar='--max',
        type=int,
        default=100,
        help='the maximum number of coins per coin type to be generated')

    return parser.parse_args()


# Return the current number of coins
def get_total_count(coin_counts):

    return sum(coin_counts.values())


# Return the current dollar amount sum for the given coin counts
def get_total_amount(coin_counts):

    return round(sum((
        coin_counts['quarters'] * QUARTER_VALUE,
        coin_counts['dimes'] * DIME_VALUE,
        coin_counts['nickels'] * NICKEL_VALUE,
        coin_counts['pennies'] * PENNY_VALUE)), 2)


def generate_input(min_count, max_count):

    coin_counts = {
        'pennies': random.randint(min_count, max_count),
        'nickels': random.randint(min_count, max_count),
        'dimes': random.randint(min_count, max_count),
        'quarters': random.randint(min_count, max_count)
    }

    return {
        # random.randint() returns a random integer within the specifie range
        # (inclusive)
        'count': get_total_count(coin_counts),
        # random.uniform() returns a random floating-point number within the
        # specified range (inclusive)
        'amount': get_total_amount(coin_counts)
    }


# Run a single round by generating random input and passing it to both player
# programs
def run_round(players, min_count, max_count, timeout):
    input_data = generate_input(min_count, max_count)
    for player in players:
        try:
            if not player.program.isalive():
                continue
            player.program.sendline(json.dumps(input_data))
            player.program.expect('\0')
            output_data = json.loads(player.program.buffer.strip())
            if (get_total_count(output_data) == input_data['count'] and
                    get_total_amount(output_data) == input_data['amount']):
                player.total_correct += 1
            else:
                player.total_incorrect += 1
        except pexpect.exceptions.TIMEOUT:
            print('program {} has timed out'.format(
                player.program.args[0].decode('utf-8')))
        except Exception as error:
            player.total_error += 1
            print('error for program {}: {}'.format(
                player.program.args[0].decode('utf-8'),
                error))


def main():

    try:
        params = parse_cli_args()
        while True:
            run_round(**vars(params))
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    main()
