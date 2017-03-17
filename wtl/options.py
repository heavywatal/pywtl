#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""For running a program in various parameters
"""
import itertools
import datetime
import re

from os import getpid
from collections import OrderedDict
from .shell import map_async, cpu_count


def optionize(key, value):
    if len(key) > 1:
        return '--{}={}'.format(key, value)
    else:
        return '-{}{}'.format(key, value)


def sequential(params, repeat=1):
    for (key, vals) in params.items():
        for value in vals:
            for i in range(repeat):
                yield optionize(key, value)


def product(params, repeat=1):
    for vals in itertools.product(*params.values()):
        args = []
        for (key, value) in zip(params.keys(), vals):
            args.append(optionize(key, value))
        for i in range(repeat):
            yield args


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


def now(sep='T', timespec='minutes', remove=r'\W'):
    dt = datetime.datetime.now()
    iso = dt.isoformat(sep, timespec)
    if remove:
        return re.sub(remove, '', iso)
    else:
        return iso


def demo():
    const = ['a.out', '-v']
    params = OrderedDict()
    params['D'] = [format(x, '02d') for x in [2, 3]]
    params['u'] = [format(x, '.2f') for x in [0.01, 0.1]]
    suffix = '_{}_{}'.format(now(), getpid())
    for i, x in enumerate(product(params, 2)):
        label = join(x) + suffix + '_{:02}'.format(i)
        yield const + x + ['--outdir=' + label]


if __name__ == '__main__':
    import inspect
    print(inspect.getsource(demo))
    print('>>> map_async(demo(), cpu_count(), dry_run=True)')
    map_async(demo(), cpu_count(), dry_run=True)
