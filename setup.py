import sys
import subprocess

packages = ['aiohttp', 'aiohttp_jinja2', 'faker']

if sys.version_info[0] < 3:
	raise Exception('Must be using Python 3')

for package in packages:
	subprocess.check_call(['pip', 'install', package])



