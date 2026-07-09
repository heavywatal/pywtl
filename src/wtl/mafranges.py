"""Convert ranges of MAF to BED."""

import re
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

from . import cli


def readiter(infile: Path) -> Iterator[str]:
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


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("infile", type=Path)
    parser.add_argument("outfile", nargs="?", type=Path)
    args = parser.parse_args()
    with args.outfile.open("w") if args.outfile else nullcontext(sys.stdout) as fout:
        for x in readiter(args.infile):
            print(x, file=fout)


if __name__ == "__main__":
    main()
