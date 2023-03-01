#!/usr/bin/env python3
"""
mafRanges in.maf db out.bed
"""
import argparse
import re
import sys
from pathlib import Path


def readiter(infile: Path):
    pattern = r"a score=([\d.]+)\ns (\S+)\.(\S+)\s+(\d+)\s+(\d+)\s+(\S+)"
    with open(infile, "r") as fin:
        for mobj in re.finditer(pattern, fin.read()):
            (score, _species, chrom, start, size, strand) = mobj.groups()
            score = int(float(score))
            start = int(start)
            size = int(size)
            end = start + size
            yield f"{chrom}\t{start}\t{end}\t{chrom}.{start}\t{score}\t{strand}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("infile", type=Path)
    parser.add_argument(
        "outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    args = parser.parse_args()
    for x in readiter(args.infile):
        print(x, file=args.outfile)


if __name__ == "__main__":
    main()