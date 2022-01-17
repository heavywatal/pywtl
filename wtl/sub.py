"""
"""
import re
import shutil


def sub(
    pattern: str,
    repl: str,
    files: list[str],
    dry_run: bool = False,
    line_number: bool = False,
):
    rex = re.compile(pattern)
    if not repl:
        repl = pattern
        dry_run = True
    for filename in files:
        try:
            with open(filename, "r+") as fio:
                product: list[str] = []
                subn_lines: list[str] = []
                subn_sum = 0
                for (i, line) in enumerate(fio.readlines()):
                    (subn_line, n) = rex.subn(repl, line)
                    product.append(subn_line)
                    if n > 0:
                        subn_sum += n
                        emphline = rex.sub(emphasize(repl), line)
                        if line_number:
                            ol = ":".join([filename, str(i + 1), emphline])
                        else:
                            ol = ":".join([filename, emphline])
                        subn_lines.append(ol)
                if subn_sum > 0:
                    if not dry_run:
                        shutil.copy2(filename, filename + "~")
                        fio.seek(0)
                        fio.write("".join(product))
                        fio.truncate()
                    if subn_lines:
                        print("".join(subn_lines).rstrip("\n"))
        except IOError as error:
            print(error)
    return


def emphasize(s: str):
    return f"\033[1m{s}\033[0m"


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--line-number", action="store_true")
    parser.add_argument("-s", "--dry-run", action="store_true")
    parser.add_argument("-r", "--repl")
    parser.add_argument("pattern")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    sub(args.pattern, args.repl, args.files, args.dry_run, args.line_number)


if __name__ == "__main__":
    main()
