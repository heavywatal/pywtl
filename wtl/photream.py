"""
Sort "Photos Library" by date
"""
import csv
import logging
import os
import re
import shutil
from pathlib import Path

from . import cli

_log = logging.getLogger(__name__)


def main():
    pictures_dir = Path("~/Pictures").expanduser()
    photoslibrary = pictures_dir / "Photos Library.photoslibrary"
    originals_dir = photoslibrary / "originals"
    outdir = pictures_dir / "PhotosArchive"
    latest_csv = max(pictures_dir.glob("PhotosLibrary_*.csv"))
    parser = cli.ArgumentParser()
    parser.add_argument("-l", "--lib", type=Path, default=originals_dir)
    parser.add_argument("-c", "--csv", type=Path, default=latest_csv)
    parser.add_argument("-o", "--outdir", type=Path, default=outdir)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        test_old_backup(pictures_dir / "PhotosBackup", args.lib, args.csv)
        return
    for src, reldst in iter_src_reldst(args.lib, args.csv):
        dst: Path = args.outdir / with_suffix_lower(reldst)
        if not dst.exists():
            _log.info(f"'{dst}'")
            if not cli.dry_run:
                dst.parent.mkdir(exist_ok=True)
                shutil.copy2(src, dst)


def test_old_backup(old_backup_dir: Path, orig_dir: Path, library_csv: Path):
    ls_photosbackup = {x.name: x for x in old_backup_dir.glob("20*")}
    not_in_photosbackup: list[Path] = []
    for original, dst in iter_src_reldst(orig_dir, library_csv):
        if not (old_backup_dir / dst.name).exists():
            not_in_photosbackup.append(original)
        else:
            ls_photosbackup.pop(dst.name)
    for x in sorted(ls_photosbackup.values()):
        print(f"{x}")
    _log.info(f"{len(not_in_photosbackup) = }")
    _log.info(f"{len(ls_photosbackup) = }")
    if not cli.dry_run:
        outdir = old_backup_dir.parent / f"{old_backup_dir.name}_only"
        outdir.mkdir(exist_ok=True)
        for name, path in ls_photosbackup.items():
            link = outdir / name
            if not link.exists():
                link.symlink_to(path)


def iter_src_reldst(topdir: Path, library_csv: Path):
    table = load_csv(library_csv)
    for original in iter_images(topdir):
        item = table.pop(original.stem, None)
        if item:
            dstname = make_filename(item["time"], item["name"])
            year = dstname.split("-", 1)[0]
            yield (original, Path(f"{year}/{dstname}"))
        else:
            _log.warning(f"no record for '{original}'")
    for item in table.values():
        _log.warning(f"no file for {item}")


def load_csv(library_csv: Path):
    _log.info(f"{library_csv}")
    table: dict[str, dict[str, str]] = {}
    with library_csv.open("r") as fin:
        for row in csv.DictReader(fin):
            uuid = row["uuid"]
            uuid_stem = uuid.removesuffix("/L0/001")
            table[uuid_stem] = row
    _log.info(f"{len(table)} records")
    return table


def iter_images(topdir: Path):
    patt = re.compile(r"jpe?g$|png$|heic$", re.IGNORECASE)
    for root, _, files in os.walk(topdir):
        for afile in files:
            if patt.search(afile):
                yield Path(root) / afile
            else:
                _log.debug(f"ignoring '{Path(root) / afile}'")


def make_filename(isotime: str, img_name: str) -> str:
    time = isotime.replace(":", "-")
    name = Path(img_name)
    return f"{time}_{name}"


def with_suffix_lower(path: Path) -> Path:
    return path.with_suffix(path.suffix.lower())


if __name__ == "__main__":
    main()
