"""
copy images from Photo Stream to one place
"""
import os
import re
import shutil
import datetime

from PIL import Image, ExifTags

APPSUPP = os.path.expanduser("~/Library/Application Support")
ASSETS = os.path.join(APPSUPP, "iLifeAssetManagement/assets")
PHOTOS = os.path.expanduser("~/Pictures/Photos Library.photoslibrary/Masters")


def ls_recursive(topdir: str = PHOTOS):
    patt = re.compile(r"jpg$|png$", re.IGNORECASE)
    paths: list[str] = []
    for root, _, files in os.walk(topdir):
        for afile in files:
            if patt.search(afile):
                paths.append(os.path.join(root, afile))
    return sorted(paths, key=os.path.basename)


def decode_exif(image: Image.Image):
    ret: dict[str, str] = dict()
    exif: dict[int, str] = image._getexif()
    for tag, value in exif.items():
        key = ExifTags.TAGS.get(tag)
        if key:
            ret[key] = value
    return ret


def parse_filename(src: str):
    mobj = re.search(r"(pub|sub-shared|watch)/", src)
    if mobj:
        label = mobj.group(1)[0]
    else:
        label = ""
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


def transfer(src: str, dst: str, delete: bool = False, dry_run: bool = False):
    func = shutil.move if delete else shutil.copy2
    if os.path.exists(dst):
        # temporal code
        if delete and os.path.basename(src) != os.path.basename(dst):
            print("duplicate: " + " ".join([src, dst]))
            if not dry_run:
                os.remove(src)
    else:
        print([src, dst])
        if not dry_run:
            func(src, dst)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-d", "--delete", action="store_true")
    parser.add_argument("-i", "--iphoto", action="store_true")
    parser.add_argument("-o", "--outdir", default=os.path.expanduser("~/tmp"))
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    if args.files:
        for src in args.files:
            dst = os.path.join(args.outdir, parse_filename(src))
            transfer(src, dst, args.delete, args.dry_run)
    elif args.iphoto:
        assert not args.delete
        outdir = os.path.expanduser("~/Pictures/PhotoStream")
        assets = ("pub", "sub", "sub-shared", "watch")
        for label in assets:
            top = os.path.join(ASSETS, label)
            for src in ls_recursive(top):
                dst = os.path.join(outdir, parse_filename(src))
                transfer(src, dst, args.delete, args.dry_run)
    else:
        assert not args.delete
        outdir = os.path.expanduser("~/Pictures/PhotosBackup")
        for src in ls_recursive():
            dst = os.path.join(outdir, parse_filename(src))
            transfer(src, dst, args.delete, args.dry_run)


if __name__ == "__main__":
    main()
