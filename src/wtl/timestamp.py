import datetime
import logging
import subprocess
from pathlib import Path

import yaml

from . import cli

_log = logging.getLogger(__name__.replace("__main__", "_"))


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("file", nargs="+", type=Path)
    args = parser.parse_args()
    for file in args.file:
        date = get_fm_date(file)
        if date is not None:
            write_iso(date, file)
            set_ctime(date, file)


def write_iso(date: datetime.datetime, file: Path) -> None:
    with file.open("rb") as fin:
        lines = fin.readlines()
    for i, line in enumerate(lines):
        if i == 0:
            assert line.startswith(b"---")
            continue
        if line.startswith(b"---"):
            msg = f"date not found in {file}"
            raise ValueError(msg)
        if line.startswith(b"date:"):
            lines[i] = f"date: {date.isoformat()}\n".encode()
            _log.debug(lines[i].decode().rstrip())
            break
    if not cli.dry_run:
        with file.open("wb") as fout:
            fout.writelines(lines)


def set_ctime(time: datetime.datetime, file: Path) -> None:
    str_time = time.strftime("%Y%m%d%H%M.%S")
    args = ["/usr/bin/touch", "-t", str_time, str(file)]
    _log.info(" ".join(args))
    if not cli.dry_run:
        subprocess.run(args, check=True)


def get_fm_date(file: Path) -> datetime.datetime | None:
    fm = read_frontmatter(file)
    obj = yaml.safe_load(fm)
    date: datetime.datetime = obj.get("date")
    if date:
        date = date.replace(microsecond=0)
        tz = datetime.timezone(datetime.timedelta(hours=9))
        return date.astimezone(tz)
    return None


def read_frontmatter(file: Path) -> bytes:
    lines: list[bytes] = []
    with file.open("rb") as fin:
        line1 = fin.readline()
        assert line1.startswith(b"---")
        for line in fin:
            if line.startswith(b"---"):
                break
            lines.append(line)
    return b"".join(lines)


if __name__ == "__main__":
    main()
