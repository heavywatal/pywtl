"""Filter bibtex entries with aux citations."""

import argparse
import logging
from pathlib import Path

from . import aux, bib

_log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=Path)
    parser.add_argument("bib", type=Path)
    parser.add_argument("aux", type=Path)
    args = parser.parse_args()
    with args.aux.open("r") as fin:
        auxkeys = aux.collect_citekeys(fin.read())
    with args.bib.open("r") as fin:
        entries = bib.read_entries(fin)
    entries = [x for x in entries if x.key in auxkeys]
    bibkeys = {x.key for x in entries}
    assert len(entries) == len(bibkeys)
    notfound = auxkeys - bibkeys
    if notfound:
        _log.warning(f"Entry not found: {notfound}")
    with args.outfile.open("w") as fout:
        fout.writelines(str(x) for x in entries)


if __name__ == "__main__":
    main()
