"""Generate CSS via Iconify API for Hugo with Sass.

Icon sets are read from a file or stdin in TOML format like this:
```
[[sets]]
prefix = "bi"
icons = ["file", "folder"]

[[sets]]
prefix = "mdi"
icons = ["home", "user"]
```
"""

import argparse
import logging
import re
import tomllib
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterable

import requests

from wtl import cli

_log = logging.getLogger(__name__)


class IconSet(TypedDict):
    prefix: str
    icons: list[str]


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-o", "--outdir", type=Path, default=Path())
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"), default="-")
    args = parser.parse_args()
    toml = args.infile.read()
    args.infile.close()
    sets: Iterable[IconSet] = tomllib.loads(toml)["sets"]
    _log.info(f"{sets = }")
    make_index_scss(args.outdir, [x["prefix"] for x in sets])
    for item in sets:
        prefix = item["prefix"]
        outfile = args.outdir / f"{prefix}.css"
        css = fetch_css(prefix, item["icons"])
        _log.debug(f"{css}")
        css = postprocess(css)
        if not cli.dry_run:
            with outfile.open("w") as fout:
                fout.write(css)
        print(outfile)


def make_index_scss(outdir: Path, names: Iterable[str]) -> None:
    outfile = outdir / "_index.scss"
    if not cli.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)
        with outfile.open("w") as fout:
            for prefix in names:
                fout.write(f'@forward "{prefix}";\n')
    print(outfile)


def fetch_css(prefix: str, icons: Iterable[str]) -> str:
    url = f"https://api.iconify.design/{prefix}.css"
    params = {
        "icons": f"{','.join(icons)}",
        "commonSelector": "commonSelector",
        "iconSelector": "iconify-icon[icon=@{prefix}:{name}@]",
    }
    if cli.dry_run:
        return url + "?" + urllib.parse.urlencode(params)
    response = requests.get(url, params=params, timeout=5)
    return response.text


def postprocess(css: str) -> str:
    css = re.sub(r"@([\w-]+:[\w-]+)@", r'"\1"', css)
    css = re.sub(r"commonSelector[^}]+}\n*", "", css)
    css = re.sub(r"\n+", "\n", css)
    return css  # noqa: RET504


if __name__ == "__main__":
    main()
