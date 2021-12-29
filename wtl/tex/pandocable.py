"""Workadound for Pandoc
"""
import pathlib
import pprint
import re
from . import aux


def resolve_ref(content, labelmap):
    def repl(mobj):
        return labelmap[mobj.group(1)]
    return re.sub(r'\\ref{([^}]+)}', repl, content)


def figure_table(content, labelmap):
    """
    - Remove asterisks from {table*} and {figure*}
    - Add labels to captions
    """
    content = re.sub(r'{(table|figure)\*}', r'{\1}', content)

    def repl(mobj):
        type = classify_label(mobj.group(2))
        num = labelmap[mobj.group(2)]
        return f'caption{{\\textbf{{{type} {num}}}. {mobj.group(1)}'
    return re.sub(r'caption{(.+?)\\label{([^}]+)}', repl, content, flags=re.S)


def classify_label(label: str):
    label = label.lower()
    if label.startswith('fig'):
        return 'Figure'
    elif label.startswith('tab'):
        return 'Table'
    return 'Equation???'


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=pathlib.Path)
    args = parser.parse_args()
    texfile = args.infile
    auxfile = texfile.with_suffix('.aux')
    with auxfile.open() as fin:
        labelmap = aux.collect_labels(fin.read())
    pprint.pprint(labelmap)
    with texfile.open() as fin:
        content = fin.read()
    content = resolve_ref(content, labelmap)
    content = figure_table(content, labelmap)
    outfile = texfile.with_suffix('.pandoc.tex')
    print(f'Writing {outfile}')
    with outfile.open('w') as fout:
        fout.write(content)


if __name__ == '__main__':
    main()
