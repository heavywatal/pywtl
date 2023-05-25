"""
"""
import argparse
import logging
from pathlib import Path

from wtl import cli

_log = logging.getLogger(__name__)


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("-i", "--infile", type=Path, default=__file__)
    parser.add_argument("outfile", nargs="?", type=argparse.FileType("w"), default="-")
    args = parser.parse_args()
    fun(args.infile)
    with args.infile.open() as fin:
        args.outfile.write(fin.read())


def fun(infile: Path):
    outfile = infile.with_suffix(".suffix")
    _log.debug(f"{infile = }")
    _log.info(f"{outfile = }")


if __name__ == "__main__":
    main()
