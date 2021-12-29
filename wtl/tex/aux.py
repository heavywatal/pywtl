"""Parse aux file
"""
import sys
import re
from collections import OrderedDict


def collect_citekeys(content):
    patt = re.compile(r'\\citation{(.+?)}')
    keys = set()
    for mobj in patt.finditer(content):
        keys.update(mobj.group(1).split(','))
    return keys


def collect_labels(content):
    patt = re.compile(r'\\newlabel{(.+?)}{{([^}]+)}')
    labels = OrderedDict()
    for mobj in patt.finditer(content):
        labels[mobj.group(1)] = mobj.group(2)
    return labels


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', default=sys.stdin,
                        type=argparse.FileType('r'))
    args = parser.parse_args()
    items = collect_citekeys(args.infile.read())
    print(items)


if __name__ == '__main__':
    main()
