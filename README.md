# Coin Problem

*Copyright 2019-2022 Caleb Evans*  
*Released under the MIT license*

## Inspiration

This project was inspired by a math problem posed to *Parade* magazine's
Marilyn Vos Savant in November 2019:

> In a contest, a friend guessed the exact number of coins in a jar: 1,692. She
> won all of the coins, which totaled $100.54. They consisted of pennies,
> nickels, dimes and quarters. How many coins of each kind were in the jar?

*Source:* https://parade.com/951440/marilynvossavant/can-you-solve-this-coin-riddle/

This project serves as a generalized solver program given any number of coins
and any dollar amount.

## Usage

### Set up virtualenv

```sh
virtualenv --python=python3 .virtualenv
source .virtualenv/bin/activate
pip install -r requirements.txt
```

### Run solver program

```sh
python -m coinproblem -c 1692 -a 100.54
```

#### Options

- `--total-coin-count` / `-c`: The total number of coins (_i.e._ the coin
  count)
- `--total-coin-amount` / `-a`: the total dollar value of all coins combined
  (_i.e._ the coin amount)

### Run duel program

The referee program accepts a variable number of executables that will be pit
against each other. The referee program _must_ be run as a module via the
`python -m` command.

Please refer to the [Player Program Specification](SPEC.md) to learn how to
write your own player programs.

```sh
python -m coinproblem.referee ./coinproblem/my-player.py
```

### Options

- `--timeout` / `-t` (default: 10): The number of seconds each player will run before timing
  out
- `--min-count` / `--min` (default: 0): The minimum number of coins per coin type to be
  generated
- `--max-count`/ `--max` (default: 100): The maximum number of coins per coin
  type to be generated

### Run tests

```sh
nose2 --quiet
```

To add additional test cases, please append an array of `[penny, nickel, dime, quarter]` counts to the JSON array in `test_cases.json`.
