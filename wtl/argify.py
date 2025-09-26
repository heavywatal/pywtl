"""Convert clippson JSON to command line arguments."""

import argparse
import json
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
    parser.add_argument("infile", nargs="?", default="-", type=argparse.FileType("r"))
    args = parser.parse_args()
    obj = json.load(args.infile)
    result = argify(obj)
    print(" ".join(result))


if __name__ == "__main__":
    main()
