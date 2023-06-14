"""Simple wrapper for OpenPBS."""
import logging
import re
from pathlib import Path

from aligons.util import cli

_log = logging.getLogger(__name__)


def main(argv: list[str] | None = None):
    parser = cli.ArgumentParser()
    parser.add_argument("-N", "--name")
    parser.add_argument("-m", "--mem", type=int, default=1)
    parser.add_argument("command", nargs="+")
    args = parser.parse_args(argv or None)
    generate_qsub_sh(args.command, args.name, args.jobs, args.mem)


def generate_qsub_sh(
    command: list[str], name: str | None = None, ncpus: int = 1, mem: int = 1
):
    assert ncpus > 0
    assert mem > 0
    name = name or auto_name("_".join(command))
    options = pbs_options(name, ncpus, mem)
    directives = [f"#PBS {key} {val}" for key, val in options.items()]
    command = add_header_footer(command)
    content = "\n".join(["#!/bin/bash", *directives, "", *command])
    _log.debug(content)
    outfile = Path(f"qsub-{name}.sh")
    _log.info(f"{outfile}")
    if not cli.dry_run:
        with outfile.open("wt") as fout:
            fout.write(content)


def auto_name(command: str):
    return re.sub(r"[ \t\n-.]+", "-", command)


def pbs_options(name: str, ncpus: int, mem: int) -> dict[str, str]:
    return {
        "-S": "/bin/bash",
        "-N": name,
        "-l": f"select=1:ncpus={ncpus}:mem={mem}gb",
    }


def add_header_footer(command: list[str]):
    header = ["hostname", "cd $PBS_O_WORKDIR", "pwd", "date -Iseconds"]
    footer = ["date -Iseconds"]
    return [*header, "", *command, "", *footer]


if __name__ == "__main__":
    main()
