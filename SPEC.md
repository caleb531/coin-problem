# Coin Problem Solver: Program Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [[RFC2119](https://www.ietf.org/rfc/rfc2119.txt)].

## Requirements

### Execution

Each program file MUST be marked as executable (i.e. `chmod +x`). If
applicable, remember to specify a shebang (`#!`) line fo your program.

### Input

Each program file MUST accept as stdin a JSON object in the following format:

```json
{"count":1692,"amount":100.54}
```

In the above example, the value `1692` can be any arbitrary integer greater than
zero. Furthermore, the value `100.54` can be any arbitrary floating-point number
greater than zero. These numbers will not exceed 2^16 - 1 (or 65,535).

A trailing newline MAY follow the output JSON, if it aids the player program's
implementation. However, the output JSON MUST NOT contain any whitespace.

The program MUST NOT make any assumptions about the key order of the input JSON.

### Output

Upon receiving the input JSON object, the program must perform its computation
and print to stdout a JSON object in the following format:

```json
{"pennies":1,"nickels":2,"dimes":3,"quarters":4}
```

In the above example, the values `1`, `2`, `3`, and `4` can be any arbitrary
integers greater than or equal to zero. These integers will not exceed 2^16 - 1
(or 65,535).

The output JSON MUST be preceded by a NUL character (`\0` or `\u0000`).

A trailing newline MAY follow the output JSON, if it aids the player program's
implementation. However, the output JSON MUST NOT contain any whitespace.

The program MUST NOT make any assumptions about the key order of the output
JSON.
