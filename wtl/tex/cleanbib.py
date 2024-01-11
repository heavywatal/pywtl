"""Remove meta data of Bibdesk."""
import argparse
import re
import sys


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
    parser.add_argument(
        "-o", "--outfile", type=argparse.FileType("w"), default=sys.stdout
    )
    parser.add_argument("infile", type=argparse.FileType("r"))
    args = parser.parse_args()
    content = args.infile.read()
    content = rm_comment(content)
    content = rm_annote(content)
    content = rename(content)
    args.outfile.write(content)


if __name__ == "__main__":
    main()
