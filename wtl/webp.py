#!/usr/bin/env python3
"""
"""
import logging
from pathlib import Path

from . import cli
from .shell import cpu_count, map_async

_log = logging.getLogger(__name__)


def magick(infile: Path, quality: int = 0):
    outfile = infile.with_suffix(".webp")
    command: list[str] = ["magick", str(infile)]
    command.extend(["-auto-orient", "-strip"])
    if quality:
        command.extend(["-quality", str(quality)])
    command.append(str(outfile))
    return command


def cwebp(infile: Path, lossless: bool = True):
    outfile = infile.with_suffix(".webp")
    command: list[str] = ["cwebp", str(infile)]
    if lossless:
        command.append("-lossless")
    command.extend(["-o", str(outfile)])
    return command


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=cpu_count())
    parser.add_argument("-q", "--quality", type=int, default=0)
    parser.add_argument("infile", nargs="*", type=Path)
    args = parser.parse_args()
    commands: list[list[str]] = []
    for infile in args.infile:
        if infile.suffix.lower() in [".jpg", ".jpeg"]:
            commands.append(magick(infile, quality=args.quality))
        else:
            commands.append(cwebp(infile))
    map_async(commands, args.jobs, outdir="")


if __name__ == "__main__":
    main()
