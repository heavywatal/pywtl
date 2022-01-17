"""Post messages to Slack with Incoming WebHooks
"""
import json
import os
import pkgutil
import socket
import subprocess
import sys

import requests


def report(message: str = "", channel: str = "", icon: str = "", dry_run: bool = False):
    lines = [" ".join(sys.argv)]
    if message:
        lines.append(message)
    post("\n".join(lines), channel=channel, icon=icon, dry_run=dry_run)


def post(text: str, channel: str = "", icon: str = "", dry_run: bool = False):
    data = {
        "username": "pywtl@" + socket.gethostname(),
        "icon_emoji": icon or ":snake:",
        "text": text,
    }
    if channel:
        data["channel"] = channel
    payload = json.dumps(data)
    if dry_run:
        print(payload)
        print(webhook_url())
    else:
        response = requests.post(webhook_url(), data=payload)
        print(f"{response.status_code=}")
        print(f"{response.reason=}")


def webhook_url():
    encrypted = pkgutil.get_data("wtl", "slack_webhook_url")
    assert encrypted is not None
    password = os.environ["SLACK_WEBHOOK"]
    return sslenc(encrypted.decode(), password, decrypt=True)


def sslenc(content: str, password: str, decrypt: bool = False):
    cmd = ["openssl", "enc", "-aes256", "-a", "-A"]
    if decrypt:
        cmd.append("-d")
    cmd.extend(["-pass", f"pass:{password}"])
    p = subprocess.run(cmd, input=content, stdout=subprocess.PIPE, text=True)
    return p.stdout


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-c", "--channel")
    parser.add_argument("-i", "--icon")
    parser.add_argument("text", nargs="*", default=["Hello!"])
    args = parser.parse_args()
    text = "\n".join(args.text)
    post(text, channel=args.channel, icon=args.icon, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
