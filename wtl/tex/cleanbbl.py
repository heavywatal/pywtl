#!/usr/bin/env python
"""
"""
import re

abbrevs = [
    'Acad', 'Adv', 'Am', 'Ann', 'Annu', 'Appl',
    'Biol', 'Biosci', 'Br', 'Bull',
    'Chem', 'Clin', 'Commun', 'Comp', 'Comput', 'Curr',
    'Dev', 'Differ', 'Dyn',
    'Ecol', 'Eng', 'Engl', 'Environ', 'Evol', 'Exp', 'Front',
    'Genet', 'Hered', 'Int', 'Interdiscip', 'J', 'Lett', 'Lond',
    'Math', 'Med', 'Mol', 'Microbiol', 'N', 'Nat', 'Natl',
    'Oncol', 'Opin', 'Philos', 'Phys', 'Popul', 'Proc',
    'R', 'Relat', 'Rep', 'Res', 'Rev',
    'Sci', 'Soc', 'Stat', 'Syst', 'Theor', 'Trans', 'Zool']


def sub_pagerange(string):
    def repl(mobj):
        (start, end) = mobj.groups()
        if int(start) > int(end):
            end = start[:-len(end)] + end
            return '{}--{}'.format(start, end)
        else:
            return mobj.group()
    return re.sub(r'(\d+)--(\d+)', repl, string)


def sub_abbrev(string):
    string = re.sub(r'\bU\s+S\s+A\b', 'USA', string)
    patt = '(' + '|'.join(abbrevs) + r')(?=\s)'
    return re.sub(patt, r'\1.', string)


def sub_command(string):
    string = re.sub(r'{\\rm\s*', r'\\textrm{', string)
    string = re.sub(r'{\\bf\s*', r'\\textbf{', string)
    string = re.sub(r'{\\it\s*', r'\\textit{', string)
    string = re.sub(r'{\\em\s*', r'\\textit{', string)
    return string


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('bbl', type=argparse.FileType('r+'))
    args = parser.parse_args()
    content = args.bbl.read()
    args.bbl.seek(0)
    content = sub_pagerange(content)
    content = sub_abbrev(content)
    content = sub_command(content)
    args.bbl.write(content)
    args.bbl.truncate()


if __name__ == '__main__':
    main()
