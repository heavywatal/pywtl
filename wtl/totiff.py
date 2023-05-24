"""
Convert image to TIFF with LZW algorithm (for PLOS manuscript)
http://journals.plos.org/ploscompbiol/s/figures
"""
import os

from PIL import Image

min_width = 789
text_width = 1560
max_width = 2250
max_height = 2625


def remove_alpha(img: Image.Image, bg_color: tuple[int, int, int] = (255, 255, 255)):
    """
    Alpha composition makes smoother edges than img.convert('RGB')
    """
    img_rgb = Image.new("RGB", img.size, bg_color)
    alpha_layer = img.split()[3]
    img_rgb.paste(img, mask=alpha_layer)
    return img_rgb


def compress(infile: str):
    img = Image.open(infile)
    img = remove_alpha(img)
    print(f"{infile} [{img.size[0]}x{img.size[1]}]")
    (base, _) = os.path.splitext(infile)
    outfile = os.path.basename(base) + ".tif"
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    print(f"\t=> {outfile} [{img.size[0]}x{img.size[1]}]")
    img.save(outfile, compression="tiff_lzw", dpi=(300.0, 300.0))
    # only float values for dpi
    # https://github.com/python-pillow/Pillow/issues/1765


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("infile", nargs="*")
    args = parser.parse_args()
    for x in args.infile:
        compress(x)


if __name__ == "__main__":
    main()
