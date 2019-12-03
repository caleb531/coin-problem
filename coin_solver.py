#!/usr/bin/env python3

import collections
import math
import itertools


# Constants
PENNY_VALUE = 0.01
NICKEL_VALUE = 0.05
DIME_VALUE = 0.1
QUARTER_VALUE = 0.25

AMOUNT_VALUES = [PENNY_VALUE, NICKEL_VALUE, DIME_VALUE, QUARTER_VALUE]

# The order of coin types that maps to the sequence of values
COIN_TYPES = ['pennies', 'nickels', 'dimes', 'quarters']

# A map of known dollar amounts (under $1) and the coin combinations known to
# sum to those respective amounts; the structure is an OrderedDict with the
# keys sorted from smallest to largest; each row of additions/subtractions must
# sum to zero
COIN_SUMS = collections.OrderedDict(sorted({
    0.05: {'quarters': 0, 'dimes': +1, 'nickels': -1},
    0.10: {'quarters': 1, 'dimes': -2, 'nickels': +1},
    0.15: {'quarters': 1, 'dimes': -1, 'nickels': -0},
    0.20: {'quarters': 1, 'dimes': -0, 'nickels': -1},
    0.25: {'quarters': 1, 'dimes': +1, 'nickels': -2},
    0.35: {'quarters': 2, 'dimes': -1, 'nickels': -1},
    0.45: {'quarters': 3, 'dimes': -3, 'nickels': -0},
    0.55: {'quarters': 3, 'dimes': -1, 'nickels': -2},
    0.65: {'quarters': 4, 'dimes': -3, 'nickels': -1},
    0.75: {'quarters': 4, 'dimes': -1, 'nickels': -3},
    0.85: {'quarters': 5, 'dimes': -3, 'nickels': -2},
    0.95: {'quarters': 5, 'dimes': -3, 'nickels': -0}
}.items()))


# Return the current number of coins
def get_current_count(coin_counts):

    return sum(coin_counts.values())


# Return the current dollar amount sum for the given coin counts
def get_current_amount(coin_counts):

    return round(sum((
        coin_counts['quarters'] * QUARTER_VALUE,
        coin_counts['dimes'] * DIME_VALUE,
        coin_counts['nickels'] * NICKEL_VALUE,
        coin_counts['pennies'] * PENNY_VALUE)), 2)


# Compute the required number of pennies by using the least-significant decimal
# digit of the total amount
def get_penny_count(total_coin_amount):

    adjusted_coin_amount = round(total_coin_amount * 10, 2)
    return round(
        (adjusted_coin_amount - math.floor(adjusted_coin_amount)) * 10) % 5


# Repeatedly replace a type of coin with another type of coin, until the
# current coin amount equals the given total
def converge_to_amount(coin_counts, total_coin_amount,
                       coin_to_replace, coin_to_replace_with):

    while (get_current_amount(coin_counts) > total_coin_amount and
           coin_counts[coin_to_replace] > 0):
        coin_counts[coin_to_replace] -= 1
        coin_counts[coin_to_replace_with] += 1


# The convergence above isn't perfect; the remaining diff is typically
# less than a dollar, so to narrow in on that exact value with greater
# precision, perform coin substitions that are known to achieve that diff
def perform_adjustment_substitutions(coin_counts, total_coin_amount):

    current_amount = get_current_amount(coin_counts)
    amount_diff = round(total_coin_amount - current_amount, 2)

    if amount_diff == 0:
        return

    # If remaining difference is a multiple of a key in the COIN_SUMS table,
    # adjust the current coin counts according to that respective sum
    for coin_sum, coin_combination in reversed(COIN_SUMS.items()):
        if round(amount_diff % coin_sum, 2) == 0:
            for coin_type, coin_diff in coin_combination.items():
                coin_counts[coin_type] += (coin_diff *
                                           int(amount_diff // coin_sum))
            break


def get_partial_sums(count):

    map = collections.defaultdict(list)
    sums = set()

    for i in range(count + 1):
        for j in range(count + 1):
            partial_sum = count - (i + j)
            map[i + j].append((i, j))
            if partial_sum in map:
                for x, y in map[partial_sum]:
                    sums.update(itertools.permutations((i, j, x, y)))

    return sums


# Search all possible permutations of coin counts until a satisfactory
# permutation is found
def brute_force(coin_counts, total_coin_count, total_coin_amount):

    count_permutations = get_partial_sums(total_coin_count)
    counts_list = next(
        p for p in count_permutations
        if round(sum(c * v for c, v in zip(p, AMOUNT_VALUES)), 2)
        == total_coin_amount)
    coin_counts.update(
        {coin_type: coin_count
         for coin_count, coin_type in zip(counts_list, COIN_TYPES)})


# Return a JSON object of coin counts
def get_coin_counts(total_coin_count, total_coin_amount):

    coin_counts = {}
    coin_counts['pennies'] = get_penny_count(total_coin_amount)

    coin_counts['quarters'] = (total_coin_count - coin_counts['pennies']) // 3
    coin_counts['dimes'] = (total_coin_count - coin_counts['pennies']) // 3
    coin_counts['nickels'] = (total_coin_count - coin_counts['pennies']) // 3
    coin_counts['nickels'] += total_coin_count - get_current_count(coin_counts)

    # Convert to the specified total amount as closely as possible
    converge_to_amount(
        coin_counts=coin_counts,
        total_coin_amount=total_coin_amount,
        coin_to_replace='quarters',
        coin_to_replace_with='dimes')
    converge_to_amount(
        coin_counts=coin_counts,
        total_coin_amount=total_coin_amount,
        coin_to_replace='dimes',
        coin_to_replace_with='nickels')

    # Make minor adjustments to land on the exact value
    perform_adjustment_substitutions(
        coin_counts=coin_counts,
        total_coin_amount=total_coin_amount)

    # If amount is still not correct, fall back to the brute force approach
    if (get_current_count(coin_counts) != total_coin_count
            or get_current_amount(coin_counts) != total_coin_amount
            or any(count < 0 for count in coin_counts.values())):
        brute_force(
            coin_counts=coin_counts,
            total_coin_count=total_coin_count,
            total_coin_amount=total_coin_amount)

    return coin_counts
