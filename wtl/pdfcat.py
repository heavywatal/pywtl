#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concatenate PDFs
"""
from PyPDF2 import PdfFileMerger, PdfFileReader


def cat(infiles, outfile):
    merger = PdfFileMerger()
    for infile in infiles:
        print(infile)
        with open(infile, 'rb') as fin:
            merger.append(PdfFileReader(fin))
    print('Writing ' + outfile)
    merger.write(outfile)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', default='_merged.pdf')
    parser.add_argument('infile', nargs='+')
    args = parser.parse_args()
    cat(args.infile, args.outfile)


if __name__ == '__main__':
    main()
