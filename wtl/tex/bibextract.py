"""Extract entries from bib file."""
import argparse
import re
import sys
from typing import TextIO


def bib_entries(file: TextIO, keys: list[str]) -> list[str]:
    entries = file.read().strip().split("\n\n")
    if keys:
        pattern = "@(?:[Aa]rticle|[Bb]ook){(" + "|".join(keys) + "),"
        return [x + "\n\n" for x in entries if re.match(pattern, x)]
    return [x + "\n\n" for x in entries]


def bbl_keys(file: TextIO) -> list[str]:
    content = file.read()
    return re.findall(r"(?<=\\bibitem\[[^\]]+?\]){([^}]+?)}", content, re.S)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--outfile", type=argparse.FileType("w"), default=sys.stdout
    )
    parser.add_argument("-b", "--bbl", type=argparse.FileType("r"))
    parser.add_argument("bib", type=argparse.FileType("r"))
    parser.add_argument("keys", nargs="*")
    args = parser.parse_args()
    keys = args.keys
    if args.bbl:
        keys.extend(bbl_keys(args.bbl))
    print(keys, file=sys.stderr)
    print(len(keys), file=sys.stderr)
    matched = bib_entries(args.bib, keys)
    print(len(matched), file=sys.stderr)
    args.outfile.writelines(matched)


if __name__ == "__main__":
    main()
