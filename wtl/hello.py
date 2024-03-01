"""Sample module."""

import getpass
import site
import sys


def main() -> None:
    print(f"Hello, {getpass.getuser()}!")
    print(f"{__file__=}")
    print(f"{sys.executable=}")
    print(f"{site.USER_BASE=}")
    print(f"{site.USER_SITE=}")
    print(f"{site.getsitepackages()=}")


if __name__ == "__main__":
    main()
