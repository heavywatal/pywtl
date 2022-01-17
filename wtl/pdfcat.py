"""Concatenate PDFs
"""
import subprocess


def gs_pdfwrite(infiles: list[str], outputfile: str, quiet: bool = False):
    args = ["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite"]
    if quiet:
        args.append("-q")
    args.append(f"-sOutputFile={outputfile}")
    args.extend(infiles)
    print(" ".join(args))
    subprocess.run(args)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", default="_merged.pdf")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("infiles", nargs="+")
    args = parser.parse_args()
    gs_pdfwrite(args.infiles, args.outfile, not args.verbose)


if __name__ == "__main__":
    main()
