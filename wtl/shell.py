#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Concurrent shell execution
"""
import concurrent.futures as confu
import multiprocessing as mp
import subprocess


def run(command):
    return subprocess.run(command, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, shell=True)


def map(commands, max_workers=mp.cpu_count()):
    with confu.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run, cmd) for cmd in commands]
        for future in confu.as_completed(futures):
            completed = future.result()
            print([completed.args, completed.returncode])
            print(completed.stdout.decode(), end='')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--jobs', type=int, default=mp.cpu_count())
    parser.add_argument('command', nargs='+')
    args = parser.parse_args()
    map(args.command, args.jobs)


if __name__ == '__main__':
    main()
