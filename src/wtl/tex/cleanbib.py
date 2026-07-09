"""Remove meta data of Bibdesk."""

import argparse
import re
import sys
from contextlib import nullcontext
from pathlib import Path


def rm_comment(string: str) -> str:
    pattern = r"@comment{.+?}\s*$"
    string = re.sub(pattern, "", string, flags=re.DOTALL | re.MULTILINE)
    string = re.sub("^%%.+?$", "", string, flags=re.MULTILINE)
    return string.lstrip()


def rm_annote(string: str) -> str:
    """Be careful when using {braces} or other special characters."""
    return re.sub(r",\s+Annote = {.*?}(?=[,}])", "", string, flags=re.DOTALL)


def rename(string: str) -> str:
    patt = "(Doi|Isbn|Issn|Month)( = )"
    return re.sub(patt, r"\1-x\2", string, flags=re.DOTALL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=Path)
    parser.add_argument("infile", type=Path)
    args = parser.parse_args()
    with args.infile.open("r") if args.infile else nullcontext(sys.stdin) as fin:
        content = fin.read()
    content = rm_comment(content)
    content = rm_annote(content)
    content = rename(content)
    with args.outfile.open("w") as fout:
        fout.write(content)


if __name__ == "__main__":
    main()
