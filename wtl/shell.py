#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Concurrent shell execution
"""
import concurrent.futures as confu
import subprocess
import re
import os

try:
    import psutil

    def cpu_count():
        return psutil.cpu_count(logical=False)
except ImportError:
    print("Warning: psutil is missing; cpu_count(logical=True)")
    from os import cpu_count


def run(command, dry_run=False, **popenargs):
    if not isinstance(command, str):
        command = ' '.join(command)
    if re.search(r'\brm\b', command):
        print(command)
        raise ValueError('rm is not allowed')
    jobname = re.sub(r'\s+-', '-', command)
    jobname = re.sub(r'[^\w\-]+', '_', jobname).strip('_')
    jobname += ".{}".format(os.getpid())
    if dry_run:
        command = '#' + command
    return jobname, subprocess.run(
        command, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, **popenargs)


def map_async(commands, max_workers=cpu_count(),
              dry_run=False, verbose=False,
              outdir='.'):
    if outdir:
        assert os.path.exists(outdir)
    with confu.ThreadPoolExecutor(max_workers=max_workers) as executor:
        fs = [executor.submit(run, cmd, dry_run) for cmd in commands]
        for future in confu.as_completed(fs):
            jobname, completed = future.result()
            print([completed.args, completed.returncode])
            output = completed.stdout
            if verbose:
                print(output.decode(), end='')
            if outdir and output:
                outfile = os.path.join(outdir, jobname + '.txt')
                with open(outfile, 'ab') as fout:
                    fout.write(output)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--jobs', type=int, default=cpu_count())
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--outdir')
    parser.add_argument('command', nargs='+')
    args = parser.parse_args()
    print('cpu_count(): {}'.format(cpu_count()))
    map_async(args.command, args.jobs, args.dry_run, args.verbose, args.outdir)


if __name__ == '__main__':
    main()
