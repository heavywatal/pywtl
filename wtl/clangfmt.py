import logging
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from . import cli

_log = logging.getLogger(__name__.replace("__main__", "_"))

presets = ["LLVM", "GNU", "Google", "Chromium", "Microsoft", "Mozilla", "Webkit"]


def main():
    user_config = Path("~/.clang-format").expanduser()
    parser = cli.ArgumentParser()
    parser.add_argument("-f", "--file", type=Path, default=user_config)
    args = parser.parse_args()
    with args.file.open("rb") as fin:
        obj = yaml.safe_load(fin)
    cnt = count(collect(obj))
    ordered = cnt.most_common()
    print(ordered)
    base_name = obj.get("BasedOnStyle", "LLVM")
    base = clang_format_dump_config(base_name)
    differed = diff(obj, base)
    print(yaml.safe_dump(differed))


def collect(config: dict[str, Any]):
    configs = {x: clang_format_dump_config(x) for x in presets}
    res: dict[str, Any] = {}
    for key, value in config.items():
        if key == "BasedOnStyle":
            continue
        friends: list[str] = []
        for name, obj in configs.items():
            if value == obj.get(key):
                friends.append(name)
        res[key] = friends
    return res


def count(collected: dict[str, list[str]]) -> Counter[str]:
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


def diff(lhs: dict[str, Any], rhs: dict[str, Any]):
    differed: dict[str, Any] = {}
    for key, value in lhs.items():
        if key == "BasedOnStyle":
            continue
        if value != rhs.get(key):
            differed[key] = f"{value}  # {rhs.get(key)}"
    return differed


def clang_format_dump_config(style: str) -> dict[str, Any]:
    assert style in presets
    args = ["clang-format", f"--style={style}", "--dump-config"]
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
        assert p.stdout is not None
        return yaml.safe_load(p.stdout)


if __name__ == "__main__":
    main()
