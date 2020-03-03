"""Alternative grep with Python re
"""
import re
import sys


def grep(pattern, infile, group, line_number, invert_match):
    rex = re.compile(pattern)
    for i, line in enumerate(infile):
        mobj = rex.search(line)
        if mobj:
            if invert_match:
                continue
            if line_number:
                print(i, end=':')
            if group is None:
                print(line, end='')
            else:
                print(mobj.group(group))
        elif invert_match:
            if line_number:
                print(i, end=':')
            print(line, end='')


def try_int(value):
    try:
        value = int(value)
    except ValueError:
        pass
    return value


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--invert-match', action='store_true')
    parser.add_argument('-n', '--line-number', action='store_true')
    parser.add_argument('-g', '--group', type=try_int)
    parser.add_argument('pattern')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    args = parser.parse_args()
    grep(args.pattern, args.infile, args.group,
         args.line_number, args.invert_match)


if __name__ == '__main__':
    main()
