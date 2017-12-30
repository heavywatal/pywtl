#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""For running a program in various parameters
"""
import itertools
import datetime
import os
import re

from collections import OrderedDict
from .shell import map_async, cpu_count


def sequential(axes: dict):
    for (key, vals) in axes.items():
        for value in vals:
            yield OrderedDict({key: value})


def product(axes: dict):
    for vals in itertools.product(*axes.values()):
        yield OrderedDict((k, v) for k, v in zip(axes.keys(), vals))


def parallel(axes: dict):
    for vals in zip(*axes.values()):
        yield OrderedDict((k, v) for k, v in zip(axes.keys(), vals))


def cycle(iterable, n=2):
    lst = list(iterable)
    for i in range(n):
        for x in lst:
            yield x


def tandem(iterable, n=2):
    for x in iterable:
        for i in range(n):
            yield x


def optionize(key, value):
    if len(key) > 1:
        return '--{}={}'.format(key, value)
    else:
        return '-{}{}'.format(key, value)


def make_args(values: dict):
    return [optionize(k, v) for (k, v) in values.items()]


def join(args):
    label = '_'.join([s.lstrip('-') for s in args])
    return label.replace('.', '').replace('=', '')


def today(remove=r'\W'):
    d = datetime.date.today()
    iso = d.isoformat()
    if remove:
        return re.sub(remove, '', iso)
    else:
        return iso


def now(sep='T', timespec='seconds', remove=r'\W'):
    dt = datetime.datetime.now()
    iso = dt.isoformat(sep, timespec)
    if remove:
        return re.sub(remove, '', iso)
    else:
        return iso


def demo():
    const = ['a.out', '-v']
    axes = OrderedDict()
    axes['D'] = [format(x, '02d') for x in [2, 3]]
    axes['u'] = [format(x, '.2f') for x in [0.01, 0.1]]
    suffix = '_{}_{}'.format(now(), os.getpid())
    for i, x in enumerate(tandem(product(axes), 2)):
        args = make_args(x)
        label = join(args) + suffix + '_{:02}'.format(i)
        yield const + args + ['--outdir=' + label]


if __name__ == '__main__':
    import inspect
    print(inspect.getsource(demo))
    print('>>> map_async(demo(), cpu_count(), dry_run=True)')
    map_async(demo(), cpu_count(), dry_run=True)
