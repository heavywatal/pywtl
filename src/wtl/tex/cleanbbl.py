import argparse
import re
from pathlib import Path

abbrevs = [
    "Acad",
    "Adv",
    "Am",
    "Ann",
    "Annu",
    "Appl",
    "Biol",
    "Biosci",
    "Br",
    "Bull",
    "Chem",
    "Clin",
    "Commun",
    "Comp",
    "Comput",
    "Curr",
    "Dev",
    "Differ",
    "Dyn",
    "Ecol",
    "Eng",
    "Engl",
    "Environ",
    "Evol",
    "Exp",
    "Front",
    "Genet",
    "Hered",
    "Int",
    "Interdiscip",
    "J",
    "Lett",
    "Lond",
    "Math",
    "Med",
    "Mol",
    "Microbiol",
    "N",
    "Nat",
    "Natl",
    "Oncol",
    "Opin",
    "Philos",
    "Phys",
    "Popul",
    "Proc",
    "R",
    "Relat",
    "Rep",
    "Res",
    "Rev",
    "Sci",
    "Soc",
    "Stat",
    "Syst",
    "Theor",
    "Trans",
    "Zool",
]


def sub_pagerange(string: str) -> str:
    def repl(mobj: re.Match[str]) -> str:
        (start, end) = mobj.groups()
        if int(start) > int(end):
            end = start[: -len(end)] + end
            return f"{start}--{end}"
        return mobj.group()

    return re.sub(r"(\d+)--(\d+)", repl, string)


def sub_abbrev(string: str) -> str:
    string = re.sub(r"\bU\s+S\s+A\b", "USA", string)
    patt = "(" + "|".join(abbrevs) + r")(?=\s)"
    return re.sub(patt, r"\1.", string)


def sub_command(string: str) -> str:
    string = re.sub(r"{\\rm\s*", r"\\textrm{", string)
    string = re.sub(r"{\\bf\s*", r"\\textbf{", string)
    string = re.sub(r"{\\it\s*", r"\\textit{", string)
    string = re.sub(r"{\\em\s*", r"\\textit{", string)
    return string  # noqa: RET504


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bbl", type=Path)
    args = parser.parse_args()
    with args.bbl.open("r+") as bbl_file:
        content = bbl_file.read()
        bbl_file.seek(0)
        content = sub_pagerange(content)
        content = sub_abbrev(content)
        content = sub_command(content)
        bbl_file.write(content)
        bbl_file.truncate()


if __name__ == "__main__":
    main()
