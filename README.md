# Coin Problem

*Copyright 2019-2021 Caleb Evans*  
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

### Run program

```sh
./__main__.py -c 1692 -a 100.54
```

#### Options

- `-c`: The total number of coins (_i.e._ the coin count)
- `-a` the total dollar value of all coins combined (_i.e._ the coin amount)

### Run tests

```sh
./tests.py
```

To add additional test cases, please append an array of `[penny, nickel, dime quarter]` counts to the JSON array in `test_cases.json`.
