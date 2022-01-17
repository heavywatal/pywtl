import random
import string


def generate_password(length: int = 42):
    letters = string.ascii_letters + string.digits + string.punctuation
    table = str.maketrans("", "", "\\\"'")
    letters = letters.translate(table)
    return "".join(random.choices(letters, k=length))


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("length", nargs="?", type=int, default=42)
    args = parser.parse_args()
    print(generate_password(args.length))


if __name__ == "__main__":
    main()
