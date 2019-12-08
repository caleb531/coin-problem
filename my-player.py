#!/usr/bin/env python3

import json

import coin_solver


def main():

    try:
        while True:
            count, amount = input('').split(',')
            coin_counts = coin_solver.get_coin_counts(
                total_coin_count=int(count),
                total_coin_amount=float(amount))
            print('\0' + json.dumps(coin_counts, separators=(',', ':')))
    except Exception:
        print('\0{}')


if __name__ == '__main__':
    main()
