#!/usr/bin/env python3

import itertools
import json
import unittest
from collections import namedtuple

import coin_solver


# Constants
PENNY_VALUE = 0.01
NICKEL_VALUE = 0.05
DIME_VALUE = 0.1
QUARTER_VALUE = 0.25

AMOUNTS_LIST = [PENNY_VALUE, NICKEL_VALUE, DIME_VALUE, QUARTER_VALUE]

CoinCounts = namedtuple('CoinCounts', [
    'pennies',
    'nickels',
    'dimes',
    'quarters'
])


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
        counts = coin_solver.get_coin_counts(
            total_coin_count=total_count,
            total_coin_amount=total_amount)
        current_count = self.get_current_count(counts)
        current_amount = self.get_current_amount(counts)
        counts_tuple = CoinCounts(**counts)
        self.assertEqual(current_count, total_count, counts_tuple)
        self.assertEqual(current_amount, total_amount, counts_tuple)
        self.assertTrue(all(count >= 0 for count in counts.values()),
                        f'coin count is negative: {counts_tuple}')

    def test_handpicked(self):
        with open('test_cases.json', 'r') as test_cases_file:
            test_cases = json.load(test_cases_file)
            for counts_list in test_cases:
                with self.subTest(counts=counts_list):
                    self.assert_single_test_case(counts_list)

    def test_permutations(self):
        for counts_list in itertools.product(range(9), repeat=4):
            with self.subTest(counts=counts_list):
                self.assert_single_test_case(counts_list)


if __name__ == '__main__':
    unittest.main()
