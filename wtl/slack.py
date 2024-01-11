"""Post messages to Slack with Incoming WebHooks."""
import json
import os
import pkgutil
import socket
import subprocess
import sys

import requests

from . import cli


def report(message: str = "", channel: str = "", icon: str = "") -> None:
    lines = [" ".join(sys.argv)]
    if message:
        lines.append(message)
    post("\n".join(lines), channel=channel, icon=icon)


def post(text: str, channel: str = "", icon: str = "") -> None:
    data = {
        "username": "pywtl@" + socket.gethostname(),
        "icon_emoji": icon or ":snake:",
        "text": text,
    }
    if channel:
        data["channel"] = channel
    payload = json.dumps(data)
    if cli.dry_run:
        print(payload)
        print(webhook_url())
    else:
        response = requests.post(webhook_url(), data=payload, timeout=32)
        print(f"{response.status_code=}")
        print(f"{response.reason=}")


def webhook_url() -> str:
    encrypted = pkgutil.get_data("wtl", "slack_webhook_url")
    assert encrypted is not None
    password = os.environ["SLACK_WEBHOOK"]
    return sslenc(encrypted.decode(), password, decrypt=True)


def sslenc(content: str, password: str, *, decrypt: bool = False) -> str:
    cmd = ["openssl", "enc", "-aes256", "-md", "md5", "-a", "-A"]
    if decrypt:
        cmd.append("-d")
    cmd.extend(["-pass", f"pass:{password}"])
    p = subprocess.run(
        cmd, input=content, stdout=subprocess.PIPE, text=True, check=True
    )
    return p.stdout


def main() -> None:
    parser = cli.ArgumentParser()
    parser.add_argument("-c", "--channel")
    parser.add_argument("-i", "--icon")
    parser.add_argument("text", nargs="*", default=["Hello!"])
    args = parser.parse_args()
    text = "\n".join(args.text)
    post(text, channel=args.channel, icon=args.icon)


if __name__ == "__main__":
    main()
