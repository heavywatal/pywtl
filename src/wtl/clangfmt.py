import logging
import subprocess
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from . import cli

_log = logging.getLogger(__name__.replace("__main__", "_"))

presets = ["LLVM", "GNU", "Google", "Chromium", "Microsoft", "Mozilla", "Webkit"]


def main() -> None:
    user_config = Path("~/.clang-format").expanduser()
    parser = cli.ArgumentParser()
    parser.add_argument("-c", "--config", action="store_true")
    parser.add_argument("file", nargs="+", type=Path)
    args = parser.parse_args()
    if args.config:
        check_config(user_config)
        return
    for f in args.file:
        fmtdiff(f)


def check_config(file: Path) -> None:
    with file.open("rb") as fin:
        obj = yaml.safe_load(fin)
    cnt = count(collect(obj))
    ordered = cnt.most_common()
    print(ordered)
    base_name = obj.get("BasedOnStyle", "LLVM")
    base = clang_format_dump_config(base_name)
    diffs = config_diff(obj, base)
    print(yaml.safe_dump(diffs))


def collect(config: Mapping[str, Any]) -> dict[str, list[str]]:
    configs = {x: clang_format_dump_config(x) for x in presets}
    res: dict[str, list[str]] = {}
    for key, value in config.items():
        if key == "BasedOnStyle":
            continue
        friends: list[str] = []
        for name, obj in configs.items():
            if value == obj.get(key):
                friends.append(name)
        res[key] = friends
    return res


def count(collected: Mapping[str, list[str]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    uniform: list[str] = []
    len_presets = len(presets)
    half_len = len_presets // 2
    for key, styles in collected.items():
        if len(styles) == len_presets:
            uniform.append(key)
            continue
        counter.update(styles)
        if len(styles) <= half_len:
            _log.warning(f"{key}: {styles}")
    if uniform:
        _log.warning(f"{uniform = }")
    return counter


def config_diff(lhs: Mapping[str, Any], rhs: Mapping[str, Any]) -> dict[str, str]:
    diffs: dict[str, str] = {}
    for key, value in lhs.items():
        if key == "BasedOnStyle":
            continue
        if value != rhs.get(key):
            diffs[key] = f"{value}  # {rhs.get(key)}"
    return diffs


def clang_format_dump_config(style: str) -> dict[str, Any]:
    assert style in presets
    args = ["clang-format", f"--style={style}", "--dump-config"]
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
        assert p.stdout is not None
        return yaml.safe_load(p.stdout)


def fmtdiff(file: Path) -> None:
    fargs: list[str | Path] = ["clang-format", file]
    dargs: list[str | Path] = ["diff", "-u", "--color", file, "-"]
    with (
        subprocess.Popen(fargs, stdout=subprocess.PIPE) as pfmt,
        subprocess.Popen(dargs, stdin=pfmt.stdout) as pdiff,
    ):
        pdiff.communicate()


if __name__ == "__main__":
    main()
