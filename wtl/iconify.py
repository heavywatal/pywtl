"""Generate CSS via Iconify API for Hugo with Sass."""

import logging
import re
import subprocess
import tomllib
import urllib.parse
from collections.abc import Iterable
from pathlib import Path

import requests

from wtl import cli

_log = logging.getLogger(__name__)


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing files."
    )
    parser.add_argument(
        "-i", "--infile", type=Path, help="TOML file. Otherwise read from hugo config."
    )
    parser.add_argument("-o", "--outdir", type=Path, default=Path())
    args = parser.parse_args()
    sets = read_config(args.infile)
    if not cli.dry_run:
        args.outdir.mkdir(parents=True, exist_ok=True)
        make_index_scss(args.outdir, sets.keys())
    for prefix, icons in sets.items():
        outfile = args.outdir / f"{prefix}.css"
        if outfile.exists() and not args.force:
            _log.info(f"{outfile} already exists.")
            continue
        css = fetch_css(prefix, icons)
        css = postprocess(css)
        if not cli.dry_run:
            with outfile.open("w") as fout:
                fout.write(css)


def make_index_scss(outdir: Path, names: Iterable[str]) -> None:
    index_scss = outdir / "_index.scss"
    with index_scss.open("w") as fout:
        for name in names:
            fout.write(f'@forward "{name}";\n')


def fetch_css(prefix: str, icons: list[str]) -> str:
    url = f"https://api.iconify.design/{prefix}.css"
    params = {
        "icons": f"{','.join(icons)}",
        "commonSelector": "commonSelector",
        "iconSelector": "iconify-icon[icon=@{prefix}:{name}@]",
    }
    if cli.dry_run:
        unparsed = url + "?" + urllib.parse.urlencode(params)
        print(unparsed)
        return unparsed
    response = requests.get(url, params=params, timeout=5)
    return response.text


def postprocess(css: str) -> str:
    css = re.sub(r"@([\w-]+:[\w-]+)@", r'"\1"', css)
    css = re.sub(r"commonSelector[^}]+}\n*", "", css)
    css = re.sub(r"\n+", "\n", css)
    return css  # noqa: RET504


def read_config(infile: Path | None) -> dict[str, list[str]]:
    """Read icon sets from Hugo configuration in TOML format.

    Icons should be listed by prefix in the `params.iconify` section, e.g.:
    ```
    [params.iconify]
    bi = ["file", "folder"]
    mdi = ["home", "user"]
    ```
    """
    if infile is None:
        cmd = ["hugo", "config"]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
        toml = p.stdout.decode()
    else:
        with infile.open("rt") as fin:
            toml = fin.read()
    data = tomllib.loads(toml)
    return data.get("params", {}).get("iconify", {})


if __name__ == "__main__":
    main()
