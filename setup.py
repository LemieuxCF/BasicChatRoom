""" Script for installing packages for the webchat """
import sys
import subprocess

PACKAGES = \
    ['aiohttp',
    'aiohttp_jinja2',
    'faker',
    'aiohttp_session[aioredis]']

if sys.version_info[0] < 3:
    raise Exception('Must be using Python 3')

for package in PACKAGES:
    subprocess.check_call(['pip', 'install', package])
