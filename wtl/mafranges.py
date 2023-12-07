"""Convert ranges of MAF to BED."""
import argparse
import re
import sys
from pathlib import Path

from . import cli


def readiter(infile: Path):
    pattern = r"a score=([\d.]+)\ns (\S+)\.(\S+)\s+(\d+)\s+(\d+)\s+(\S+)"
    with infile.open("r") as fin:
        for mobj in re.finditer(pattern, fin.read()):
            (score, _species, chrom, start, size, strand) = mobj.groups()
            name = f"{chrom}.{start}"
            score = int(float(score))
            start = int(start)
            size = int(size)
            end = start + size
            yield f"{chrom}\t{start}\t{end}\t{name}\t{score}\t{strand}"


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("infile", type=Path)
    parser.add_argument(
        "outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    args = parser.parse_args()
    for x in readiter(args.infile):
        print(x, file=args.outfile)


if __name__ == "__main__":
    main()
