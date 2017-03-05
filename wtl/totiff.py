#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def compress(infile):
    img = Image.open(infile)
    print('{infile} [{img.size[0]}x{img.size[1]}]'.format(**locals()))
    (base, ext) = os.path.splitext(infile)
    outfile = os.path.basename(base) + '.lzw.tiff'
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    print('\t=> {outfile} [{img.size[0]}x{img.size[1]}]'.format(**locals()))
    img.save(outfile, compression='tiff_lzw', dpi=(300.0, 300.0))
    # only float values for dpi
    # https://github.com/python-pillow/Pillow/issues/1765


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='*')
    args = parser.parse_args()
    for x in args.infile:
        compress(x)


if __name__ == '__main__':
    main()
