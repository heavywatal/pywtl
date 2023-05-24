"""
Extract \\includegraphics{...} from TeX file and rename them (for PLOS)
http://journals.plos.org/ploscompbiol/s/figures
"""
import os
import re
import shutil
import sys


def finditer(text: str):
    pattern = r"^.*(?<!%).*\\includegraphics.*?{(\S+?)}"
    for mobj in re.finditer(pattern, text, re.M):
        yield mobj.group(1)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-i", "--indir", default="")
    parser.add_argument("-o", "--outdir", default="")
    parser.add_argument("-m", "--main", type=int, default=sys.maxsize)
    parser.add_argument(
        "infile", nargs="?", default=sys.stdin, type=argparse.FileType("r")
    )
    args = parser.parse_args()

    text = args.infile.read()
    for i, infile in enumerate(finditer(text), 1):
        (_, ext) = os.path.splitext(infile)
        if i <= args.main:
            outfile = f"Fig{i}{ext}"
        else:
            outfile = f"S{i - args.main}_Fig{ext}"
        ipath = os.path.join(args.indir, infile)
        opath = os.path.join(args.outdir, outfile)
        if args.dry_run:
            print(f'shutil.copy2("{ipath}", "{opath}")')
        else:
            shutil.copy2(ipath, opath)


if __name__ == "__main__":
    main()
