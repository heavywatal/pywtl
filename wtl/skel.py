#!/usr/bin/env python3
"""
"""
import argparse
import logging
import sys

_log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument(
        "outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    parser.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=open(__file__, "r")
    )
    args = parser.parse_args()
    args.outfile.write(args.infile.read())


if __name__ == "__main__":
    main()
