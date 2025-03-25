#!/usr/bin/python3
"""
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("username")
args = parser.parse_args()

with open('snatcher_user.sql', mode='rt') as file:
    create = file.read()

with open('snatcher_user.{username}.sql'.format(username=args.username), mode='wt') as file:
    file.write(create.format(username=args.username))

