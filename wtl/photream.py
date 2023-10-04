"""
Sort "Photos Library" by date
"""
import csv
import datetime
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

from PIL import ExifTags, Image

from . import cli

_log = logging.getLogger(__name__)
pictures_dir = Path("~/Pictures").expanduser()
photoslibrary = pictures_dir / "Photos Library.photoslibrary"
originals_dir = photoslibrary / "originals"
old_backup_dir = pictures_dir / "PhotosBackup"
latest_csv = max(pictures_dir.glob("PhotosLibrary_*.csv"))


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("--copy", action="store_true")
    parser.add_argument("library", nargs="?", type=Path, default=latest_csv)
    args = parser.parse_args()
    test()
    if args.library.suffix == ".csv":
        it = iter_csv(args.library)
    else:
        it = iter_originals_dsts(args.library)
    for src, d in it:
        dst = with_suffix_lower(d)
        if not dst.exists():
            common = os.path.commonpath([src, dst])
            relsrc = f"../../{src.relative_to(common)}"
            _log.info(f"ln -s '{relsrc}' '{dst}'")
            if not cli.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if args.copy:
                    shutil.copy2(src, dst)
                else:
                    dst.symlink_to(relsrc)


def test():
    ls_photosbackup = {x.name: x for x in old_backup_dir.glob("20*")}
    not_in_photosbackup: list[Path] = []
    for original, dst in iter_csv(latest_csv):
        if not (old_backup_dir / dst.name).exists():
            not_in_photosbackup.append(original)
        else:
            ls_photosbackup.pop(dst.name)
    for x in sorted(ls_photosbackup.values()):
        print(f"{x}")
    _log.info(f"{len(not_in_photosbackup) = }")
    _log.info(f"{len(ls_photosbackup) = }")
    if not cli.dry_run:
        (pictures_dir / "working").mkdir(exist_ok=True)
        for name, path in ls_photosbackup.items():
            link = pictures_dir / "working" / name
            if not link.exists():
                link.symlink_to(path)


def compare():
    ls1 = [x for x, _ in iter_csv(latest_csv)]
    ls2 = list(iter_originals(originals_dir))
    _log.info(f"{len(ls1) = } vs {len(ls2) = }")
    set1 = set(ls1)
    set2 = set(ls2)
    _log.info(f"{set1 - set2 = }")
    _log.info(f"{set2 - set1 = }")


def iter_csv(library_csv: Path):
    _log.info(f"{library_csv}")
    with library_csv.open("r") as fin:
        for row in csv.DictReader(fin):
            if original := find_file(row):
                dstname = make_filename(row["time"], row["name"])
                dstpath = make_dstpath(dstname)
                yield (original, dstpath)


def make_dstpath(dstname: str) -> Path:
    year = dstname.split("-", 1)[0]
    return pictures_dir / "PhotosSymlinks" / year / dstname


def find_file(item: dict[str, str]) -> Path | None:
    uuid = item["uuid"]
    uuid_stem = uuid.removesuffix("/L0/001")
    matched = list((originals_dir / uuid[0]).glob(uuid_stem + "*"))
    if not matched:
        _log.warning(f"{originals_dir}/{uuid} not found")
        return None
    if len(matched) > 1:
        matched = [x for x in matched if x.suffix not in (".aae", ".mov")]
    assert len(matched) == 1, matched
    return matched[0]


def iter_originals_dsts(topdir: Path):
    for original in iter_originals(topdir):
        yield original, old_backup_dir / parse_filename(original)


def iter_originals(topdir: Path):
    patt = re.compile(r"jpe?g$|png$|heic$", re.IGNORECASE)
    for root, _, files in os.walk(topdir):
        for afile in files:
            if patt.search(afile):
                yield Path(root) / afile


def decode_exif(image: Image.Image):
    ret: dict[str, str] = {}
    exif = image.getexif()
    for tag, value in exif.items():
        key = ExifTags.TAGS.get(tag)
        if key:
            ret[key] = value
    return ret


def parse_filename(src: Path):
    uuid = src.stem
    img_name = uuid2img(uuid)
    sec = src.stat().st_mtime
    dt = datetime.datetime.fromtimestamp(sec)
    time_stamp = dt.isoformat()
    if src.suffix.lower() in ("jpg", "jpeg"):
        time_stamp = exiftime(src) or time_stamp
    return make_filename(time_stamp, img_name)


def uuid2img(uuid: str):
    scpt = f'tell application "Photos" to get filename of media item id "{uuid}"'
    cmd = ["/usr/bin/osascript", "-e", scpt]
    _log.debug(" ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    return p.stdout.decode().strip()


def exiftime(src: Path) -> str:
    img = Image.open(src)
    exif = decode_exif(img)
    return exif.get("DateTimeOriginal", "").replace(" ", "T")


def make_filename(isotime: str, img_name: str) -> str:
    time = isotime.replace(":", "-")
    name = Path(img_name)
    return f"{time}_{name}"


def with_suffix_lower(path: Path) -> Path:
    return path.with_suffix(path.suffix.lower())


if __name__ == "__main__":
    main()
