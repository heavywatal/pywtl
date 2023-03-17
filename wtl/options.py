"""For running a program in various parameters
"""
import argparse
import itertools
import datetime
import os
import re

from collections import OrderedDict
from collections.abc import Iterable
from typing import Any
from .shell import map_async, cpu_count


def sequential(axes: dict[str, str]):
    for key, vals in axes.items():
        for value in vals:
            yield OrderedDict({key: value})


def product(axes: dict[str, list[str]]):
    for vals in itertools.product(*axes.values()):
        yield OrderedDict((k, v) for k, v in zip(axes.keys(), vals))


def parallel(axes: dict[str, str]):
    for vals in zip(*axes.values()):
        yield OrderedDict((k, v) for k, v in zip(axes.keys(), vals))


def cycle(iterable: Iterable[Any], n: int = 2):
    rep = itertools.repeat(tuple(iterable), n)
    return itertools.chain.from_iterable(rep)


def tandem(iterable: Iterable[dict[str, str]], n: int = 2):
    for x in iterable:
        for _ in range(n):
            yield x


def optionize(key: str, value: Any):
    if len(key) > 1:
        return "--{}={}".format(key, value)
    else:
        return "-{}{}".format(key, value)


def make_args(values: dict[str, str]):
    return [optionize(k, v) for (k, v) in values.items()]


def join(args: list[str]):
    label = "_".join([s.lstrip("-") for s in args])
    return label.replace(".", "").replace("=", "")


def today(remove: str = r"\W"):
    d = datetime.date.today()
    iso = d.isoformat()
    if remove:
        return re.sub(remove, "", iso)
    else:
        return iso


def now(sep: str = "T", timespec: str = "seconds", remove: str = r"\W"):
    dt = datetime.datetime.now()
    iso = dt.isoformat(sep, timespec)
    if remove:
        return re.sub(remove, "", iso)
    else:
        return iso


def demo():
    const = ["a.out", "-v"]
    axes: dict[str, list[str]] = OrderedDict()
    axes["D"] = [format(x, "02d") for x in [2, 3]]
    axes["u"] = [format(x, ".2f") for x in [0.01, 0.1]]
    suffix = "_{}_{}".format(now(), os.getpid())
    for i, x in enumerate(tandem(product(axes), 2)):
        args = make_args(x)
        label = join(args) + suffix + "_{:02}".format(i)
        yield const + args + ["--outdir=" + label]


def ArgumentParser(**kwargs: Any):
    parser = argparse.ArgumentParser(**kwargs)
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-j", "--jobs", type=int, default=cpu_count())
    parser.add_argument("-p", "--parallel", type=int, default=1)
    parser.add_argument("-r", "--repeat", type=int, default=1)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("-o", "--outdir", default=".stdout")
    return parser


if __name__ == "__main__":
    import inspect

    print(inspect.getsource(demo))
    print(">>> map_async(demo(), cpu_count(), dry_run=True)")
    map_async(demo(), cpu_count(), dry_run=True)
