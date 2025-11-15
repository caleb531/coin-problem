#!/usr/bin/env python3

import itertools
import json
from collections import namedtuple
from pathlib import Path

import pytest

import coinproblem.solver as solver

# Constants
PENNY_VALUE = 0.01
NICKEL_VALUE = 0.05
DIME_VALUE = 0.10
QUARTER_VALUE = 0.25

AMOUNTS_LIST = [PENNY_VALUE, NICKEL_VALUE, DIME_VALUE, QUARTER_VALUE]
COUNT_FIELD_NAMES = ("pennies", "nickels", "dimes", "quarters")

CoinCounts = namedtuple("CoinCounts", COUNT_FIELD_NAMES)

TEST_CASES_PATH = Path(__file__).with_name("test_cases.json")
HANDPICKED_COUNTS = json.loads(TEST_CASES_PATH.read_text())


def get_current_count(coin_counts):
    return sum(coin_counts.values())


def get_current_amount(coin_counts):
    return round(
        sum(
            (
                coin_counts["quarters"] * QUARTER_VALUE,
                coin_counts["dimes"] * DIME_VALUE,
                coin_counts["nickels"] * NICKEL_VALUE,
                coin_counts["pennies"] * PENNY_VALUE,
            )
        ),
        2,
    )


def assert_single_test_case(counts_list):
    total_count = sum(counts_list)
    total_amount = round(
        sum(count * amount for count, amount in zip(counts_list, AMOUNTS_LIST)), 2
    )
    counts = solver.get_coin_counts(
        total_coin_count=total_count, total_coin_amount=total_amount
    )
    current_count = get_current_count(counts)
    current_amount = get_current_amount(counts)
    counts_tuple = CoinCounts(**counts)
    assert current_count == total_count, (
        f"coin count mismatch: {counts_tuple}; "
        f"valid: ${total_amount}, "
        f"{total_count}, "
        f"{counts_list}"
    )
    assert current_amount == total_amount, (
        f"coin count mismatch: {counts_tuple}; "
        f"valid: ${total_amount}, "
        f"{total_count}, "
        f"{counts_list}"
    )
    assert all(count >= 0 for count in counts.values()), (
        f"coin count is negative: {counts_tuple}; "
        f"valid: ${total_amount}, "
        f"{total_count}, "
        f"{counts_list}"
    )


@pytest.mark.parametrize(
    COUNT_FIELD_NAMES,
    HANDPICKED_COUNTS,
)
def test_handpicked(pennies, nickels, dimes, quarters):
    assert_single_test_case((pennies, nickels, dimes, quarters))


@pytest.mark.parametrize(
    COUNT_FIELD_NAMES,
    tuple(itertools.product(range(15), repeat=4)),
)
def test_permutations(pennies, nickels, dimes, quarters):
    assert_single_test_case((pennies, nickels, dimes, quarters))
