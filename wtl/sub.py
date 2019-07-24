"""
"""
import re
import shutil


def sub(pattern, repl, files, dry_run=False, line_number=False):
    rex = re.compile(pattern)
    if repl is None:
        repl = pattern
        dry_run = True
    for filename in files:
        try:
            with open(filename, 'r+') as fio:
                product = []
                subn_lines = []
                subn_sum = 0
                for (i, line) in enumerate(fio.readlines()):
                    (subn_line, n) = rex.subn(repl, line)
                    product.append(subn_line)
                    if n > 0:
                        subn_sum += n
                        emphline = rex.sub(emphasize(repl or pattern), line)
                        if line_number:
                            ol = ':'.join([filename, str(i + 1), emphline])
                        else:
                            ol = ':'.join([filename, emphline])
                        subn_lines.append(ol)
                if subn_sum > 0:
                    if not dry_run:
                        shutil.copy2(filename, filename + '~')
                        fio.seek(0)
                        fio.write(''.join(product))
                        fio.truncate()
                    if subn_lines:
                        print(''.join(subn_lines).rstrip('\n'))
        except IOError as error:
            print(error)
    return


def emphasize(s):
    if hasattr(s, "__call__") and s.__name__ == "camel2snake":
        def wrap_em(mobj):
            return emphasize(camel2snake(mobj))
        s = wrap_em
    else:
        s = '\033[1m' + s + '\033[0m'
    return s


def camel2snake(matchobj):
    s = ''
    for c in matchobj.group():
        if c.isupper():
            s += '_' + c.lower()
        else:
            s += c
    return s


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--line-number", action='store_true')
    parser.add_argument("-s", "--dry-run", action='store_true')
    parser.add_argument("-r", "--repl", default=None)
    parser.add_argument("-w", "--whitespace", action='store_true')
    parser.add_argument("-c", "--decamel", action='store_const',
                        dest="repl", const=camel2snake)
    parser.add_argument("pattern")
    parser.add_argument("files", nargs='*')
    args = parser.parse_args()
    if args.whitespace:
        args.files.insert(0, args.pattern)
        args.pattern = " +$"
        args.repl = ''
    sub(args.pattern, args.repl, args.files, args.dry_run, args.line_number)


if __name__ == '__main__':
    main()
