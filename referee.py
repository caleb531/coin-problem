#!/usr/bin/env python3

import argparse
import json
import multiprocessing
import random
import time

import pexpect

from player import Player


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


# Print information for the player's current input
def print_current_input(player, count, amount):
    print(f'{player.path}: count={count}, amount=${amount}')


# Run a single round by generating random input and passing it to both player
# programs
def run_rounds_for_player(player, inputs, lock, queue):
    player.start_program()
    for current_input in inputs:
        try:
            if not player.program.isalive():
                with lock:
                    print(f'{player.path} no longer alive')
                continue
            print_current_input(player, **current_input)
            player.program.sendline(json.dumps(current_input))
            player.program.expect_exact('\0')
            output_data = json.loads(player.program.buffer.strip())
            if (get_total_count(output_data) == current_input['count'] and
                    get_total_amount(output_data) == current_input['amount']):
                player.total_correct += 1
            else:
                player.total_incorrect += 1
        except pexpect.exceptions.TIMEOUT:
            with lock:
                print(f'{player.path} has timed out')
                break
        except Exception as error:
            player.total_error += 1
            with lock:
                print(f'error for {player.path}: {error}')
    queue.put(player)


def start_processes(processes):
    for process in processes:
        process.start()


def get_results_from_players(processes):
    for process in processes:
        process.join()
        yield process.get()


def run_duel(players, min_count, max_count, timeout):
    inputs = [generate_input(min_count, max_count)
              for i in range(10_000)]

    lock = multiprocessing.RLock()
    queue = multiprocessing.Queue()

    processes = [multiprocessing.Process(
        target=run_rounds_for_player,
        args=(player, inputs, lock, queue)) for player in players]

    start_processes(processes)
    results = get_results_from_players(processes)

    return results


def main():

    try:
        params = parse_cli_args()
        run_duel(**vars(params))
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    main()
