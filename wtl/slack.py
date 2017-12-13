#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post messages to Slack with Incoming WebHooks
"""
import requests
import json
import os
import pkgutil
import subprocess


def decrypt(code):
    inkey = os.path.expanduser('~/.ssh/id_rsa')
    cmd = ['openssl', 'rsautl', '-decrypt', '-inkey', inkey]
    process = subprocess.run(cmd, input=code, stdout=subprocess.PIPE)
    return process.stdout.decode()


def post(text, dry_run=False):
    encrypted = pkgutil.get_data('wtl', 'slack_webhook_url')
    webhook_url = decrypt(encrypted)
    data = {
        'username': 'pywtl',
        'icon_emoji': ':snake:',
        'text': text,
    }
    payload = json.dumps(data)
    if dry_run:
        print(webhook_url)
        print(payload)
    else:
        response = requests.post(webhook_url, payload)
        print(response.status_code)
        print(response.text)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('text')
    args = parser.parse_args()
    post(args.text, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
