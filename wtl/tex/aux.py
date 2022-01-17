"""Parse aux file
"""
import sys
import re
from collections import OrderedDict


def collect_citekeys(content: str):
    patt = re.compile(r"\\citation{(.+?)}")
    keys: set[str] = set()
    for mobj in patt.finditer(content):
        keys.update(mobj.group(1).split(","))
    return keys


def collect_labels(content: str):
    patt = re.compile(r"\\newlabel{(.+?)}{{([^}]+)}")
    labels: dict[str, str] = OrderedDict()
    for mobj in patt.finditer(content):
        labels[mobj.group(1)] = mobj.group(2)
    return labels


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile", nargs="?", default=sys.stdin, type=argparse.FileType("r")
    )
    args = parser.parse_args()
    content = args.infile.read()
    citekeys = collect_citekeys(content)
    print(f"{citekeys=}")
    labels = collect_labels(content)
    print(f"{labels=}")


if __name__ == "__main__":
    main()
