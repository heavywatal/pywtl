"""Extract entries from bib file."""

import argparse
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from collections.abc import Iterable


def bib_entries(file: TextIO, keys: Iterable[str]) -> list[str]:
    entries = file.read().strip().split("\n\n")
    if keys:
        pattern = "@(?:[Aa]rticle|[Bb]ook){(" + "|".join(keys) + "),"
        return [x + "\n\n" for x in entries if re.match(pattern, x)]
    return [x + "\n\n" for x in entries]


def bbl_keys(file: TextIO) -> list[str]:
    content = file.read()
    return re.findall(r"(?<=\\bibitem\[[^\]]+?\]){([^}]+?)}", content, re.DOTALL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=Path)
    parser.add_argument("-b", "--bbl", type=Path)
    parser.add_argument("bib", type=Path)
    parser.add_argument("keys", nargs="*")
    args = parser.parse_args()
    keys = args.keys
    if args.bbl:
        with args.bbl.open("r") as fin:
            keys.extend(bbl_keys(fin))
    print(keys, file=sys.stderr)
    print(len(keys), file=sys.stderr)
    with args.bib.open("r") as fin:
        matched = bib_entries(fin, keys)
    print(len(matched), file=sys.stderr)
    with args.outfile.open("w") as fout:
        fout.writelines(matched)


if __name__ == "__main__":
    main()
