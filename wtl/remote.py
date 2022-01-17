"""Send pings and commands to remote hosts
"""
import sys
from .shell import map_async, cpu_count


def ping(host: str):
    if sys.platform.startswith("darwin"):
        waitopt = "t"
    else:
        waitopt = "w"
    return ["ping", "-c1", "-{}2".format(waitopt), host]


def ssh(host: str, command: str = ""):
    command = command or "date"
    return ["ssh", host, command]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=cpu_count())
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-c", "--command")
    parser.add_argument("host", nargs="+")
    args = parser.parse_args()
    if args.command:
        commands = [ssh(x, args.command) for x in args.host]
    else:
        commands = [ping(x) for x in args.host]
    map_async(
        commands, args.jobs, dry_run=args.dry_run, verbose=args.verbose, outdir=""
    )


if __name__ == "__main__":
    main()
