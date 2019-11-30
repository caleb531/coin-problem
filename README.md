# Coin Problem

*Copyright 2019 Caleb Evans*  

## Usage

### Run program

```
./__main__.py -c 1692 -a 100.54
```

#### Options

- `-c`: The total number of coins (_i.e._ the coin count)
- `-a` the total dollar value of all coins combined (_i.e._ the coin amount)

### Run tests

```
./tests.py
```

To add additional test cases, please append an array of `[penny, nickel, dime,
quarter]` counts to the JSON array in `test_cases.json`.
