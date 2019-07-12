"""Parse aux file
"""
import sys
import re


def collect_citekeys(content):
    patt = re.compile(r'\\citation{(.+?)}')
    keys = set()
    for mobj in patt.finditer(content):
        keys.update(mobj.group(1).split(','))
    return keys


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', default=sys.stdin,
                        type=argparse.FileType('r'))
    args = parser.parse_args()
    keys = collect_citekeys(args.infile.read())
    print('\n'.join(keys))


if __name__ == '__main__':
    main()
