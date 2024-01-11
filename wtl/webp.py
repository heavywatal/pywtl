import logging
import subprocess
from pathlib import Path

from . import cli

_log = logging.getLogger(__name__)


def magick(infile: Path, quality: int = 0) -> list[str]:
    outfile = infile.with_suffix(".webp")
    command: list[str] = ["magick", str(infile)]
    command.extend(["-auto-orient", "-strip"])
    if quality:
        command.extend(["-quality", str(quality)])
    command.append(str(outfile))
    return command


def cwebp(infile: Path, *, lossless: bool = True) -> list[str]:
    outfile = infile.with_suffix(".webp")
    command: list[str] = ["cwebp", str(infile)]
    if lossless:
        command.append("-lossless")
    command.extend(["-o", str(outfile)])
    return command


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-Q", "--quality", type=int, default=0)
    parser.add_argument("infile", nargs="*", type=Path)
    args = parser.parse_args()
    commands: list[list[str]] = []
    for infile in args.infile:
        if infile.suffix.lower() in [".jpg", ".jpeg"]:
            commands.append(magick(infile, quality=args.quality))
        else:
            commands.append(cwebp(infile))
    if cli.dry_run:
        for cmd in commands:
            print(" ".join(cmd))
    else:
        fs = [cli.thread_submit(subprocess.run, x, check=True) for x in commands]
        cli.wait_raise(fs)


if __name__ == "__main__":
    main()
