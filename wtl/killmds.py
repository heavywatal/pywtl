#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suppress spotlight daemons for laptop battery
"""
import subprocess
import time
import getpass


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', default=0.5)
    args = parser.parse_args()
    password = getpass.getpass()
    cmd = ['sudo', 'killall', 'mds', 'mds_stores']
    while True:
        subprocess.run(cmd, input=password.encode())
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
