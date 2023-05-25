"""
copy images from Photo Stream to one place
"""
import datetime
import os
import re
import shutil
from pathlib import Path

from PIL import ExifTags, Image

from . import cli

APPSUPP = Path("~/Library/Application Support").expanduser()
ASSETS = APPSUPP / "iLifeAssetManagement/assets"
PHOTOS = Path("~/Pictures/Photos Library.photoslibrary/Masters").expanduser()


def ls_recursive(topdir: Path = PHOTOS):
    patt = re.compile(r"jpg$|png$", re.IGNORECASE)
    paths: list[Path] = []
    for root, _, files in os.walk(topdir):
        for afile in files:
            if patt.search(afile):
                paths.append(Path(root) / afile)
    return sorted(paths, key=os.path.basename)


def decode_exif(image: Image.Image):
    ret: dict[str, str] = {}
    exif: dict[int, str] = image._getexif()  # noqa: SLF001
    for tag, value in exif.items():
        key = ExifTags.TAGS.get(tag)
        if key:
            ret[key] = value
    return ret


def parse_filename(src: str):
    mobj = re.search(r"(pub|sub-shared|watch)/", src)
    label = mobj.group(1)[0] if mobj else ""
    sec = os.path.getmtime(src)
    dt = datetime.datetime.fromtimestamp(sec)
    time_stamp = dt.isoformat()
    if src.lower().endswith("jpg"):
        img = Image.open(src)
        exif = decode_exif(img)
        exif_time = exif.get("DateTimeOriginal")
        if exif_time:
            time_stamp = exif_time.replace(" ", "T")
    time_stamp = time_stamp.replace(":", "-")
    mobj = re.search(r"([a-z]?IMG_\S+)$", src)
    assert mobj
    basename_ = mobj.group(1)
    return "_".join([time_stamp, label + basename_])


def transfer(src: Path, dst: Path, *, delete: bool = False):
    func = shutil.move if delete else shutil.copy2
    if dst.exists():
        # temporal code
        if delete and src.name != dst.name:
            print(f"duplicate: {src}, {dst}")
            if not cli.dry_run:
                src.unlink()
    else:
        print([src, dst])
        if not cli.dry_run:
            func(src, dst)


def main():
    parser = cli.ArgumentParser()
    parser.add_argument("-D", "--delete", action="store_true")
    parser.add_argument("-i", "--iphoto", action="store_true")
    parser.add_argument("-o", "--outdir", default=Path("~/tmp").expanduser(), type=Path)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args()

    if args.files:
        for src in args.files:
            dst = args.outdir / parse_filename(src.name)
            transfer(src, dst, delete=args.delete)
    elif args.iphoto:
        assert not args.delete
        outdir = Path("~/Pictures/PhotoStream").expanduser()
        assets = ("pub", "sub", "sub-shared", "watch")
        for label in assets:
            top = ASSETS / label
            for src in ls_recursive(top):
                dst = outdir / parse_filename(src.name)
                transfer(src, dst, delete=args.delete)
    else:
        assert not args.delete
        outdir = Path("~/Pictures/PhotosBackup").expanduser()
        for src in ls_recursive():
            dst = outdir / parse_filename(src.name)
            transfer(src, dst, delete=args.delete)


if __name__ == "__main__":
    main()
