"""For running a program in various parameters."""
import inspect
import itertools
import os
import re
import time
from collections import OrderedDict
from collections.abc import Iterable, Iterator
from typing import Any

from . import cli


def sequential(axes: dict[str, str]) -> Iterator[OrderedDict[str, str]]:
    for key, vals in axes.items():
        for value in vals:
            yield OrderedDict({key: value})


def product(axes: dict[str, list[str]]) -> Iterator[OrderedDict[str, str]]:
    for vals in itertools.product(*axes.values()):
        yield OrderedDict((k, v) for k, v in zip(axes.keys(), vals, strict=True))


def parallel(axes: dict[str, str]) -> Iterator[OrderedDict[str, str]]:
    for vals in zip(*axes.values(), strict=True):
        yield OrderedDict((k, v) for k, v in zip(axes.keys(), vals, strict=True))


def cycle(iterable: Iterable[Any], n: int = 2) -> Iterator[OrderedDict[str, str]]:
    rep = itertools.repeat(tuple(iterable), n)
    return itertools.chain.from_iterable(rep)


def tandem(iterable: Iterable[dict[str, str]], n: int = 2) -> Iterator[dict[str, str]]:
    for x in iterable:
        for _ in range(n):
            yield x


def optionize(key: str, value: Any) -> str:
    if len(key) > 1:
        return f"--{key}={value}"
    return f"-{key}{value}"


def make_args(values: dict[str, str]) -> list[str]:
    return [optionize(k, v) for (k, v) in values.items()]


def join(args: list[str]) -> str:
    label = "_".join([s.lstrip("-") for s in args])
    return label.replace(".", "").replace("=", "")


def today(remove: str = r"\W") -> str:
    iso = time.strftime("%F")
    if remove:
        return re.sub(remove, "", iso)
    return iso


def now(sep: str = "T", remove: str = r"\W") -> str:
    iso = time.strftime(f"%F{sep}%T")
    if remove:
        return re.sub(remove, "", iso)
    return iso


def demo() -> Iterator[list[str]]:
    const = ["a.out", "-v"]
    axes: dict[str, list[str]] = OrderedDict()
    axes["D"] = [f"{x:02}" for x in [2, 3]]
    axes["u"] = [f"{x:.2f}" for x in [0.01, 0.1]]
    suffix = f"_{now()}_{os.getpid()}"
    for i, x in enumerate(tandem(product(axes), 2)):
        args = make_args(x)
        label = join(args) + suffix + f"_{i:02}"
        yield const + args + ["--outdir=" + label]


class ArgumentParser(cli.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_argument("-r", "--repeat", type=int, default=1)
        self.add_argument("--skip", type=int, default=0)
        self.add_argument("-o", "--outdir", default=".stdout")


if __name__ == "__main__":
    parser = ArgumentParser()
    args = parser.parse_args()
    print(inspect.getsource(demo))
    for x in demo():
        print(" ".join(x))
