"""Sort "Photos Library" by date."""

import csv
import logging
import os
import re
import shutil
from collections.abc import Iterator
from pathlib import Path

from . import cli

_log = logging.getLogger(__name__)


def main() -> None:
    pictures_dir = Path("~/Pictures").expanduser()
    photoslibrary = pictures_dir / "PhotosLibrary.photoslibrary"
    originals_dir = photoslibrary / "originals"
    outdir = pictures_dir / "PhotosBackup"
    latest_csv = max(pictures_dir.glob("PhotosLibrary_*.csv"))
    parser = cli.ArgumentParser()
    parser.add_argument("-l", "--lib", type=Path, default=originals_dir)
    parser.add_argument("-c", "--csv", type=Path, default=latest_csv)
    parser.add_argument("-o", "--outdir", type=Path, default=outdir)
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        test_backup(args.outdir, args.lib, args.csv)
    else:
        do_backup(args.outdir, args.lib, args.csv)


def do_backup(backup_dir: Path, orig_dir: Path, library_csv: Path) -> None:
    for src, reldst in iter_src_reldst(orig_dir, library_csv):
        dst: Path = backup_dir / with_suffix_lower(reldst)
        if not dst.exists():
            _log.info(f"'{dst}'")
            if not cli.dry_run:
                dst.parent.mkdir(0o755, exist_ok=True)
                shutil.copy2(src, dst)


def test_backup(backup_dir: Path, orig_dir: Path, library_csv: Path) -> None:
    test_library_dups(orig_dir, library_csv)
    only_in_photosbackup = {
        with_suffix_lower(x).name: x for x in backup_dir.rglob("20*") if x.is_file()
    }
    not_in_photosbackup: list[Path] = []
    for src, reldst in iter_src_reldst(orig_dir, library_csv):
        if (backup_dir / reldst).exists():
            only_in_photosbackup.pop(with_suffix_lower(reldst).name)
        else:
            not_in_photosbackup.append(src)
    _log.info(f"{len(not_in_photosbackup) = }")
    _log.info(f"{len(only_in_photosbackup) = }")
    if not cli.dry_run:
        linkdir = backup_dir.with_name(f"{backup_dir.name}_only")
        if linkdir.exists():
            for x in linkdir.iterdir():
                x.unlink()
        else:
            linkdir.mkdir(0o755)
        for name, path in only_in_photosbackup.items():
            symlink(path, linkdir / name)
    test_backup_dups(backup_dir)


def test_library_dups(orig_dir: Path, library_csv: Path) -> None:
    dup_checker: dict[Path, list[Path]] = {}
    for src, reldst in iter_src_reldst(orig_dir, library_csv):
        dup_checker.setdefault(reldst, []).append(src)
    for reldst, srcs in dup_checker.items():
        if len(srcs) > 1:
            _log.warning(f"duplicated: {reldst}")
            for src in srcs:
                _log.info(f"{src} {src.exists()}")


def test_backup_dups(backup_dir: Path) -> None:
    counter: dict[str, list[Path]] = {}
    for path in backup_dir.rglob("20*"):
        if path.is_file():
            date = path.stem.split("T", 1)[0]
            stem = path.stem.split("_", 1)[1]
            counter.setdefault(f"{date}_{stem}", []).append(path)
    for files in counter.values():
        if len(files) > 1:
            for x in files:
                print(x)


def iter_src_reldst(orig_dir: Path, library_csv: Path) -> Iterator[tuple[Path, Path]]:
    table = load_csv(library_csv)
    for original in iter_images(orig_dir):
        uuid = original.stem
        item = table.pop(uuid, None)
        if item:
            dstname = make_filename(item["time"], item["name"])
            year = extract_year(dstname)
            yield (original, Path(f"{year}/{dstname}"))
        else:
            _log.warning(f"no record for '{original}'")
    for item in table.values():
        _log.warning(f"no file for {item}")


def load_csv(library_csv: Path) -> dict[str, dict[str, str]]:
    _log.info(f"{library_csv}")
    table: dict[str, dict[str, str]] = {}
    with library_csv.open("r") as fin:
        for row in csv.DictReader(fin):
            uuid = row["uuid"]
            uuid_stem = uuid.removesuffix("/L0/001")
            table[uuid_stem] = row
    _log.info(f"{len(table)} records")
    return table


def iter_images(directory: Path) -> Iterator[Path]:
    patt = re.compile(r"jpe?g$|png$|heic$", re.IGNORECASE)
    for root, _, files in os.walk(directory):
        for afile in files:
            if patt.search(afile):
                yield Path(root) / afile
            else:
                _log.debug(f"ignoring '{Path(root) / afile}'")


def subdir_by_year(directory: Path) -> None:
    for src in directory.rglob("20*"):
        if not src.is_file():
            continue
        year = extract_year(src.name)
        if src.parent.name == year:
            continue
        dstdir = directory / year
        _log.info(f"mv {src} {dstdir}/")
        if not cli.dry_run:
            dstdir.mkdir(0o755, exist_ok=True)
            shutil.move(src, dstdir)


def extract_year(filename: str) -> str:
    year = filename.split("-", 1)[0]
    assert 1970 < int(year) < 9999, filename  # noqa: PLR2004
    return year


def make_filename(isotime: str, img_name: str) -> str:
    time = isotime.replace(":", "-")
    return f"{time}_{img_name}"


def with_suffix_lower(path: Path) -> Path:
    return path.with_suffix(path.suffix.lower())


def symlink(src: Path, link: Path) -> Path:
    """Do not overwrite existing one unless it is a broken link."""
    if not link.exists():
        if link.is_symlink():
            link.unlink()
        link.symlink_to(src)
    return link


if __name__ == "__main__":
    main()
