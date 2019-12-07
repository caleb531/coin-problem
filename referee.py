#!/usr/bin/env python3

import argparse
import json
import random

import pexpect

import timer
from player import Player


# Constants
PENNY_VALUE = 0.01
NICKEL_VALUE = 0.05
DIME_VALUE = 0.1
QUARTER_VALUE = 0.25


# Globals
inputs = []
next_input_index = 0


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
        default=10,
        help='the number of seconds each player will run before timing out')
    parser.add_argument(
        '--min-count',
        '--min',
        metavar='--min',
        type=int,
        default=0,
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


def generate_new_input(min_count, max_count):

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


# Get the next input, either generate it on-the-fly or retrieve from file
def reset_inputs():
    global next_input_index

    next_input_index = 0


# Get the next input, either generate it on-the-fly or retrieve from file
def get_next_input(min_count, max_count):
    global inputs
    global next_input_index

    if next_input_index < len(inputs):
        next_input = inputs[next_input_index]
        next_input_index += 1
    else:
        next_input = generate_new_input(min_count, max_count)
        inputs.append(next_input)
        next_input_index += 1
    return next_input


# Print information for the player's current input
def print_next_input(player, count, amount):
    print(f'P{player.index}: count = {count}, amount = ${amount}')


# Run a single round by generating random input and passing it to both player
# programs
def run_rounds_for_player(player, min_count, max_count):
    player.start_program()
    while True:
        next_input = get_next_input(min_count, max_count)
        try:
            if not player.program.isalive():
                print(f'P{player.index} no longer alive')
                continue
            print_next_input(player, **next_input)
            player.program.sendline(json.dumps(next_input))
            player.program.expect_exact('\0')
            output_data = json.loads(player.program.buffer.strip())
            if (get_total_count(output_data) == next_input['count'] and
                    get_total_amount(output_data) == next_input['amount']):
                player.total_correct += 1
            else:
                player.total_incorrect += 1
        except pexpect.exceptions.TIMEOUT:
            print(f'P{player.index} has timed out for {next_input}')
        except timer.TimeoutError:
            print()
            print(f'referee timeout expired; ending P{player.index}')
            print()
            break
        except Exception as error:
            player.total_error += 1
            print(f'error for P{player.index}: {error}')


# Print the parameters for this duel
def print_duel_info(players, min_count, max_count, timeout):
    print(f'min count per coin type: {min_count}')
    print(f'max count per coin type: {max_count}')
    print(f'timeout per player: {timeout:,} s')
    print()
    print_player_info(players)


# Print the number and program path for each player
def print_player_info(players):
    for p, player in enumerate(players):
        player.index = p
        print(f'P{player.index}: {player.path}')
    print()


# Print the final correct/incorrect stats for each player
def print_duel_results(players):
    for p, player in enumerate(players):
        print(f'P{player.index} results:')
        print(f'  correct = {player.total_correct}')
        print(f'  incorrect = {player.total_incorrect}')
        print(f'  error = {player.total_error}')


def run_duel(players, min_count, max_count, timeout):

    print_duel_info(players, min_count, max_count, timeout)

    for player in players:
        reset_inputs()
        with timer.Timer(timeout):
            run_rounds_for_player(player, min_count, max_count)

    print_duel_results(players)

    return players


def main():

    try:
        params = parse_cli_args()
        run_duel(**vars(params))
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    main()
