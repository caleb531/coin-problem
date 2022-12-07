#!/usr/bin/env python3

import itertools
import json
import os
import os.path
import unittest
from collections import namedtuple

import coinproblem.solver as solver


# Constants
PENNY_VALUE = 0.01
NICKEL_VALUE = 0.05
DIME_VALUE = 0.10
QUARTER_VALUE = 0.25

AMOUNTS_LIST = [PENNY_VALUE, NICKEL_VALUE, DIME_VALUE, QUARTER_VALUE]

CoinCounts = namedtuple('CoinCounts', (
    'pennies',
    'nickels',
    'dimes',
    'quarters'
))


class TestCoinSolver(unittest.TestCase):

    # Return the current number of coins
    def get_current_count(self, coin_counts):
        return sum(coin_counts.values())

    # Return the current dollar amount sum for the given coin counts
    def get_current_amount(self, coin_counts):
        return round(sum((
            coin_counts['quarters'] * QUARTER_VALUE,
            coin_counts['dimes'] * DIME_VALUE,
            coin_counts['nickels'] * NICKEL_VALUE,
            coin_counts['pennies'] * PENNY_VALUE)), 2)

    def assert_single_test_case(self, counts_list):
        total_count = sum(counts_list)
        total_amount = round(sum(count * amount for count, amount in
                                 zip(counts_list, AMOUNTS_LIST)), 2)
        counts = solver.get_coin_counts(
            total_coin_count=total_count,
            total_coin_amount=total_amount)
        current_count = self.get_current_count(counts)
        current_amount = self.get_current_amount(counts)
        counts_tuple = CoinCounts(**counts)
        self.assertEqual(current_count,
                         total_count,
                         f'coin count mismatch: {counts_tuple}; '
                         f'valid: ${total_amount}, '
                         f'{total_count}, '
                         f'{counts_list}')
        self.assertEqual(current_amount,
                         total_amount,
                         f'coin count mismatch: {counts_tuple}; '
                         f'valid: ${total_amount}, '
                         f'{total_count}, '
                         f'{counts_list}')
        self.assertTrue(all(count >= 0 for count in counts.values()),
                        f'coin count is negative: {counts_tuple}; '
                        f'valid: ${total_amount}, '
                        f'{total_count}, '
                        f'{counts_list}')

    def test_handpicked(self):
        test_dir = os.path.dirname(__file__)
        test_cases_path = os.path.join(test_dir, 'test_cases.json')
        with open(test_cases_path, 'r') as test_cases_file:
            test_cases = json.load(test_cases_file)
            for counts_list in test_cases:
                yield self.assert_single_test_case, (counts_list,)

    def test_permutations(self):
        for counts_list in itertools.product(range(15), repeat=4):
            yield self.assert_single_test_case, (counts_list,)


if __name__ == '__main__':
    unittest.main()
