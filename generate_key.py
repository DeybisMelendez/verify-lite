#!/usr/bin/env python3

import argparse
import secrets


def generate_key(length: int = 8) -> str:
    chars = length // 2 * 2
    return secrets.token_hex(chars // 2).upper()[:chars]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("count", nargs="?", type=int, default=1)
    parser.add_argument("--length", type=int, default=8)
    args = parser.parse_args()

    for _ in range(args.count):
        print(generate_key(args.length))
