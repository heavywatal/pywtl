#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Concurrent shell execution
"""
import concurrent.futures as confu
import subprocess
import re

try:
    import psutil

    def cpu_count():
        return psutil.cpu_count(logical=False)
except ImportError:
    print("Warning: psutil is missing; cpu_count(logical=True)")
    from os import cpu_count


def run(command, dry_run=False):
    if not isinstance(command, str):
        command = ' '.join(command)
    if re.search(r'\brm\b', command):
        print(command)
        raise ValueError('rm is not allowed')
    if dry_run:
        command = 'echo ' + command
    return subprocess.run(command, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, shell=True)


def map(commands, max_workers=cpu_count(), dry_run=False):
    with confu.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run, cmd, dry_run) for cmd in commands]
        for future in confu.as_completed(futures):
            completed = future.result()
            print([completed.args, completed.returncode])
            print(completed.stdout.decode(), end='')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-j', '--jobs', type=int, default=cpu_count())
    parser.add_argument('command', nargs='+')
    args = parser.parse_args()
    print('cpu_count(): {}'.format(cpu_count()))
    map(args.command, args.jobs, args.dry_run)


if __name__ == '__main__':
    main()
