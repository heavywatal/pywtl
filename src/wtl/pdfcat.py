"""Concatenate PDFs."""

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

from . import cli


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=Path, default="_concatenated.pdf")
    parser.add_argument("infiles", nargs="+", type=Path)
    args = parser.parse_args()
    qpdf_empty_pages(args.infiles, args.outfile)


def qpdf_empty_pages(infiles: Iterable[Path], outfile: Path) -> None:
    args = ["qpdf", "--empty", "--pages", *infiles, "--", outfile]
    print(" ".join(str(x) for x in args))
    if not cli.dry_run:
        subprocess.run(args, check=True)


if __name__ == "__main__":
    main()
