"""
Extract \\includegraphics{...} from TeX file and rename them (for PLOS)
http://journals.plos.org/ploscompbiol/s/figures
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

from wtl import cli


def finditer(text: str):
    pattern = r"^.*(?<!%).*\\includegraphics.*?{(\S+?)}"
    for mobj in re.finditer(pattern, text, re.M):
        yield mobj.group(1)


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("-i", "--indir", default="", type=Path)
    parser.add_argument("-o", "--outdir", default="", type=Path)
    parser.add_argument("-m", "--main", type=int, default=sys.maxsize)
    parser.add_argument(
        "infile", nargs="?", default=sys.stdin, type=argparse.FileType("r")
    )
    args = parser.parse_args()

    text = args.infile.read()
    for i, infile in enumerate(finditer(text), 1):
        ext = Path(infile).suffix
        outfile = f"Fig{i}{ext}" if i <= args.main else f"S{i - args.main}_Fig{ext}"
        ipath = args.indir / infile
        opath = args.outdir / outfile
        if cli.dry_run:
            print(f'shutil.copy2("{ipath}", "{opath}")')
        else:
            shutil.copy2(ipath, opath)


if __name__ == "__main__":
    main()
