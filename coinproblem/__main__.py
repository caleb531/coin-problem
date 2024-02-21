#!/usr/bin/env python3

import argparse

import coinproblem.solver as solver


# Read and parse arguments to the CLI program
def get_cli_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--total-coin-count", "-c", type=int)

    parser.add_argument("--total-coin-amount", "-a", type=float)

    return parser.parse_args()


def main(total_coin_count, total_coin_amount):

    print("Total Coin Count:".ljust(18), f"{total_coin_count:,}")
    print("Total Coin Amount:".ljust(18), f"${total_coin_amount:.2f}")
    print()

    coin_counts = solver.get_coin_counts(total_coin_count, total_coin_amount)
    if not coin_counts:
        print("No solution")
        return

    current_coin_count = solver.get_current_count(coin_counts)
    current_coin_amount = solver.get_current_amount(coin_counts)

    print(
        "\n".join(
            f'{name.capitalize() + ":":<9}{count:,}'
            for name, count in coin_counts.items()
        )
    )

    print()
    print("Solved Coin Count:".ljust(18), f"{current_coin_count:,}")
    print("Solved Coin Amount:".ljust(18), f"${current_coin_amount:.2f}")


if __name__ == "__main__":
    main(**vars(get_cli_args()))
