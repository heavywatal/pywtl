"""Concurrent shell execution."""
import concurrent.futures as confu
import contextlib
import logging
import os
import re
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from . import cli

_log = logging.getLogger(__name__)


def run(
    command: str | list[str],
    outdir: Path = Path(),
    **popenargs: Any,
) -> subprocess.CompletedProcess[Any]:
    popenargs.setdefault("shell", True)
    popenargs.setdefault("stdout", subprocess.PIPE)
    popenargs.setdefault("stderr", subprocess.STDOUT)
    if not isinstance(command, str):
        command = " ".join(command)
    if re.search(r"\brm\b", command):
        _log.error(command)
        msg = "rm is not allowed"
        raise ValueError(msg)
    if cli.dry_run:
        command = "#" + command
    elif outdir:
        outfile = re.sub(r"\s+-", "-", command)
        outfile = re.sub(r"[^\w\-]+", "_", outfile).strip("_")
        outfile += f".{os.getpid()}.txt"
        outfile = outdir / outfile
        popenargs["stdout"] = outfile.open("ab")
    try:
        return subprocess.run(command, text=True, check=False, **popenargs)
    finally:
        with contextlib.suppress(AttributeError):
            popenargs["stdout"].close()


def map_async(
    commands: Iterable[list[str]],
    max_workers: int | None = None,
    outdir: Path = Path(),
) -> None:
    if outdir:
        assert outdir.exists(), f"{outdir} does not exist"
    with confu.ThreadPoolExecutor(max_workers=max_workers) as executor:
        fs = [executor.submit(run, cmd, outdir) for cmd in commands]
        for future in confu.as_completed(fs):
            completed = future.result()
            print([completed.args, completed.returncode])
            _log.info(completed.stdout)


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-o", "--outdir", type=Path)
    parser.add_argument("command", nargs="+")
    args = parser.parse_args()
    _log.info(f"{os.cpu_count() = }")
    map_async(args.command, args.jobs, args.outdir)


if __name__ == "__main__":
    main()
