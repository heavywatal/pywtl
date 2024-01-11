"""Filter bibtex entries with aux citations."""
import argparse
import logging
import sys

from . import aux, bib

_log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--outfile", type=argparse.FileType("w"), default=sys.stdout
    )
    parser.add_argument("bib", type=argparse.FileType("r"))
    parser.add_argument("aux", type=argparse.FileType("r"))
    args = parser.parse_args()
    auxkeys = aux.collect_citekeys(args.aux.read())
    entries = bib.read_entries(args.bib)
    entries = [x for x in entries if x.key in auxkeys]
    bibkeys = {x.key for x in entries}
    assert len(entries) == len(bibkeys)
    notfound = auxkeys - bibkeys
    if notfound:
        _log.warning(f"Entry not found: {notfound}")
    args.outfile.writelines(str(x) for x in entries)


if __name__ == "__main__":
    main()
