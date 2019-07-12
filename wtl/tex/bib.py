"""Parse bib file
"""
import re
import sys

required_keys = ['author', 'title', 'journal',
                 'year', 'volume', 'number', 'pages',
                 'publisher', 'address', 'editor']


def read_entries(file):
    patt = re.compile(r'@(?!comment).+?}$', re.DOTALL | re.MULTILINE)
    return [BibEntry(m.group(0)) for m in patt.finditer(file.read())]


class BibEntry:
    def __init__(self, string):
        (head, body) = string.split(',', 1)
        (self.type, self.key) = head.split('{', 1)
        self.tags = {}
        patt = r'(\S+)\s*=\s*({.*?})(?=[,}]$)'
        patt = re.compile(patt, re.DOTALL | re.MULTILINE)
        for mobj in patt.finditer(body):
            key = mobj.group(1).lower()
            if key in required_keys:
                value = mobj.group(2)
                if key == 'pages':
                    value = sub_pagerange(value)
                self.tags[key] = value

    def __str__(self):
        s = self.type + '{' + self.key + ',\n\t'
        s += ',\n\t'.join([' = '.join([k, v]) for k, v in self.tags.items()])
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
    parser.add_argument('-n', '--number', action='store_true')
    parser.add_argument('-k', '--keys', action='store_true')
    parser.add_argument('-o', '--outfile',
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('bib', type=argparse.FileType('r'))
    args = parser.parse_args()
    entries = read_entries(args.bib)
    if args.number:
        print(len(entries))
    elif args.keys:
        print([x._key for x in entries])
    else:
        args.outfile.writelines([str(x) for x in entries])


if __name__ == '__main__':
    main()
