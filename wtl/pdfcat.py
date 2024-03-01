"""Concatenate PDFs."""

import subprocess

from . import cli


def gs_pdfwrite(infiles: list[str], outputfile: str, *, quiet: bool = False) -> None:
    args = ["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite"]
    if quiet:
        args.append("-q")
    args.append(f"-sOutputFile={outputfile}")
    args.extend(infiles)
    print(" ".join(args))
    if not cli.dry_run:
        subprocess.run(args, check=True)


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-o", "--outfile", default="_merged.pdf")
    parser.add_argument("infiles", nargs="+")
    args = parser.parse_args()
    gs_pdfwrite(args.infiles, args.outfile, quiet=args.verbosity <= 0)


if __name__ == "__main__":
    main()
