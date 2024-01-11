"""mv with regex."""
import re
from pathlib import Path

from . import cli


def sub(pattern: str, repl: str) -> None:
    rex = re.compile(pattern)
    for oldpath in Path().iterdir():
        newname, n = rex.subn(repl, oldpath.name)
        if n:
            oldname = rex.sub(lambda m: emphasize(m[0]), oldpath.name)
            print(f"{oldname} \t-> {newname}")
            if not cli.dry_run:
                oldpath.rename(newname)


def emphasize(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("pattern")
    parser.add_argument("repl")
    args = parser.parse_args()
    sub(args.pattern, args.repl)


if __name__ == "__main__":
    main()
