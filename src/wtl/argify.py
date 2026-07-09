"""Convert clippson JSON to command line arguments."""

import argparse
import json
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def argify(obj: Mapping[str, str]) -> list[str]:
    args: list[str] = []
    for key, value in obj.items():
        if len(key) > 1:
            args.append(f"--{key}={value}")
        else:
            args.append(f"-{key} {value}")
    return args


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", nargs="?", type=Path)
    args = parser.parse_args()
    with args.infile.open("r") if args.infile else nullcontext(sys.stdin) as fin:
        obj = json.load(fin)
    result = argify(obj)
    print(" ".join(result))


if __name__ == "__main__":
    main()
