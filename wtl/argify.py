"""
Convert clippson JSON to command line arguments
"""
import json


def argify(obj: dict[str, str]):
    args: list[str] = []
    for key, value in obj.items():
        if len(key) > 1:
            args.append(f"--{key}={value}")
        else:
            args.append(f"-{key} {value}")
    return args


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("infile", nargs="?", default="-", type=argparse.FileType("r"))
    args = parser.parse_args()
    obj = json.load(args.infile)
    result = argify(obj)
    print(" ".join(result))


if __name__ == "__main__":
    main()
