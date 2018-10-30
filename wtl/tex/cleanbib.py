#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Remove meta data of Bibdesk
"""
import re
import sys


def rm_comment(string):
    pattern = r'@comment{.+?}\s*}\s*(.+?)\s*@comment{'
    mobj = re.search(pattern, string, re.DOTALL)
    return mobj.group(1) + '\n'


def rm_annote(string):
    '''Be careful when using {braces} or other special characters'''
    return re.sub(r',\s+Annote = {.*?}(?=[,}])', '', string, flags=re.DOTALL)


def rename(string):
    patt = '(Doi|Isbn|Issn|Month)( = )'
    return re.sub(patt, r'\1-x\2', string, flags=re.DOTALL)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile',
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('infile', type=argparse.FileType('r'))
    args = parser.parse_args()
    content = args.infile.read()
    content = rm_comment(content)
    content = rm_annote(content)
    content = rename(content)
    args.outfile.write(content)


if __name__ == '__main__':
    main()
