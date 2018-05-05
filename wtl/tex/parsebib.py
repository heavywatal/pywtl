#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extract entries from bib
"""
import re
import sys

required_keys = ['author', 'title', 'journal',
                 'year', 'volume', 'number', 'pages',
                 'publisher', 'address', 'editor']


def bib_entries(file):
    entries = file.read().strip().split('\n\n')
    return [x + '\n\n' for x in entries if re.match('@article|@book', x)]


class BibEntry:
    def __init__(self, string):
        mobj = re.search(r'@(?:article|book)\s*{\s*[^,\s]+', string)
        self._open = mobj.group(0)
        self._key = self._open.split('{')[1]
        self._entry = {}
        for mobj in re.finditer(r'(\S+)\s*=\s*({.*?})(?=[,}]\n)', string):
            key = mobj.group(1).lower()
            if key in required_keys:
                value = mobj.group(2)
                if key == 'pages':
                    value = sub_pagerange(value)
                self._entry[key] = value

    def __str__(self):
        s = self._open + ',\n\t'
        s += ',\n\t'.join([' = '.join([k, v]) for k, v in self._entry.items()])
        s += '}\n\n'
        return s


def sub_pagerange(string):
    def repl(mobj):
        (start, end) = mobj.groups()
        if int(start) > int(end):
            end = start[:-len(end)] + end
        return '{}--{}'.format(start, end)
    return re.sub(r'(\d+)--?(\d+)', repl, string)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile',
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('bib', type=argparse.FileType('r'))
    args = parser.parse_args()
    entries = bib_entries(args.bib)
    print(len(entries), file=sys.stderr)
    entries = [BibEntry(s) for s in entries]
    print([x._key for x in entries], file=sys.stderr)
    args.outfile.writelines([str(x) for x in entries])


if __name__ == '__main__':
    main()
