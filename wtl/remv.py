"""mv with regex
"""
import os
import re


def sub(pattern: str, repl: str, dry_run: bool = False):
    rex = re.compile(pattern)
    for current in os.listdir("."):
        if rex.search(current):
            result = rex.sub(repl, current)
            print("{0} \t-> {1}".format(current, result))
            if not dry_run:
                os.rename(current, result)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("pattern")
    parser.add_argument("repl")
    args = parser.parse_args()
    sub(args.pattern, args.repl, args.dry_run)


if __name__ == "__main__":
    main()
