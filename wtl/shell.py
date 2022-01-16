"""Concurrent shell execution
"""
import concurrent.futures as confu
import subprocess
import re
import os
import warnings

try:
    import psutil

    def cpu_count():
        return psutil.cpu_count(logical=False)

except ImportError:
    print("Warning: psutil is missing; cpu_count(logical=True)")
    from os import cpu_count


def run(command, dry_run=False, outdir=None, **popenargs):
    popenargs.setdefault("shell", True)
    popenargs.setdefault("stdout", subprocess.PIPE)
    popenargs.setdefault("stderr", subprocess.STDOUT)
    if not isinstance(command, str):
        command = " ".join(command)
    if re.search(r"\brm\b", command):
        print(command)
        raise ValueError("rm is not allowed")
    if dry_run:
        command = "#" + command
    elif outdir:
        outfile = re.sub(r"\s+-", "-", command)
        outfile = re.sub(r"[^\w\-]+", "_", outfile).strip("_")
        outfile += ".{}.txt".format(os.getpid())
        outfile = os.path.join(outdir, outfile)
        popenargs["stdout"] = open(outfile, "ab")
    try:
        return subprocess.run(command, **popenargs)
    finally:
        try:
            popenargs["stdout"].close()
        except AttributeError:
            pass


def map_async(
    commands, max_workers=cpu_count(), dry_run=False, verbose=False, outdir="."
):
    if outdir:
        assert os.path.exists(outdir), outdir + " does not exist"
    elif not verbose:
        warnings.warn("stdout/stderr will be ignored")
    with confu.ThreadPoolExecutor(max_workers=max_workers) as executor:
        fs = [executor.submit(run, cmd, dry_run, outdir) for cmd in commands]
        for future in confu.as_completed(fs):
            completed = future.result()
            print([completed.args, completed.returncode])
            if verbose and completed.stdout:
                print(completed.stdout.decode(), end="")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=cpu_count())
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o", "--outdir")
    parser.add_argument("command", nargs="+")
    args = parser.parse_args()
    print("cpu_count(): {}".format(cpu_count()))
    map_async(args.command, args.jobs, args.dry_run, args.verbose, args.outdir)


if __name__ == "__main__":
    main()
