import logging
import sys
from contextlib import nullcontext
from pathlib import Path

from wtl import cli

_log = logging.getLogger(__name__)


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-i", "--infile", type=Path, default=__file__)
    parser.add_argument("outfile", nargs="?", type=Path)
    args = parser.parse_args()
    fun(args.infile)
    with (
        args.infile.open("r") as fin,
        args.outfile.open("w") if args.outfile else nullcontext(sys.stdout) as fout,
    ):
        fout.write(fin.read())


def fun(infile: Path) -> None:
    outfile = infile.with_suffix(".suffix")
    _log.debug(f"{infile = }")
    _log.info(f"{outfile = }")


if __name__ == "__main__":
    main()
