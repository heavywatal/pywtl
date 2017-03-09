#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concatenate PDFs
"""
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter


def cat(infiles, outfile):
    merger = PdfFileMerger()
    for infile in infiles:
        print(infile)
        with open(infile, 'rb') as fin:
            merger.append(PdfFileReader(fin))
    print('Writing ' + outfile)
    merger.write(outfile)


def merge(labelfile, picturefile, outfile):
    picpage = PdfFileReader(open(picturefile, 'rb')).getPage(0)
    reader = PdfFileReader(open(labelfile, 'rb'))
    writer = PdfFileWriter()
    for labpage in reader.pages:
        writer.addPage(labpage)
        writer.addPage(picpage)
    print('Writing ' + outfile)
    with open(outfile, 'wb') as fout:
        writer.write(fout)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', default='_merged.pdf')
    parser.add_argument('-p', '--postcard')
    parser.add_argument('infile', nargs='+')
    args = parser.parse_args()

    if args.postcard:
        merge(args.infile[0], args.postcard, args.outfile)
    else:
        cat(args.infile, args.outfile)


if __name__ == '__main__':
    main()
