"""Concurrent shell execution
"""
import concurrent.futures as confu
import logging
import os
import re
import subprocess
from typing import Any, Iterable

from . import cli

_log = logging.getLogger(__name__)

try:
    import psutil

    def cpu_count() -> int | None:
        return psutil.cpu_count(logical=False)

except ImportError:
    _log.warning("psutil is missing; cpu_count(logical=True)")
    from os import cpu_count


def run(
    command: str | list[str],
    outdir: str = "",
    **popenargs: Any,
):
    popenargs.setdefault("shell", True)
    popenargs.setdefault("stdout", subprocess.PIPE)
    popenargs.setdefault("stderr", subprocess.STDOUT)
    if not isinstance(command, str):
        command = " ".join(command)
    if re.search(r"\brm\b", command):
        _log.error(command)
        raise ValueError("rm is not allowed")
    if cli.dry_run:
        command = "#" + command
    elif outdir:
        outfile = re.sub(r"\s+-", "-", command)
        outfile = re.sub(r"[^\w\-]+", "_", outfile).strip("_")
        outfile += f".{os.getpid()}.txt"
        outfile = os.path.join(outdir, outfile)
        popenargs["stdout"] = open(outfile, "ab")
    try:
        return subprocess.run(command, text=True, **popenargs)
    finally:
        try:
            popenargs["stdout"].close()
        except AttributeError:
            pass


def map_async(
    commands: Iterable[list[str]],
    max_workers: int | None = cpu_count(),
    outdir: str = "",
):
    if outdir:
        assert os.path.exists(outdir), outdir + " does not exist"
    with confu.ThreadPoolExecutor(max_workers=max_workers) as executor:
        fs = [executor.submit(run, cmd, outdir) for cmd in commands]
        for future in confu.as_completed(fs):
            completed = future.result()
            print([completed.args, completed.returncode])
            _log.info(completed.stdout)


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=cpu_count())
    parser.add_argument("-o", "--outdir")
    parser.add_argument("command", nargs="+")
    args = parser.parse_args()
    _log.info(f"{cpu_count() = }")
    map_async(args.command, args.jobs, args.outdir)


if __name__ == "__main__":
    main()
