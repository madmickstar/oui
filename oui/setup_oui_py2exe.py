#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe, sys, os, glob
from codecs import open


sys.argv.append('py2exe')

with open(os.path.join('data','oui.csv'), 'rb') as f:
    OUI_CSV = f.read()

py2exe_options = {
    'bundle_files': 1,
    'compressed': True,
    'optimize': 2,
    'packages': [],
    'dll_excludes': ['w9xpopen.exe'],           # exclude win95 98 dll files
    'includes': [],                             # additional modules
    'excludes': ['_scproxy', '_sysconfigdata']  # exluded modules
}

setup(
  options = {
            'py2exe': py2exe_options,
            },
  console = [{"script": "oui.py", "other_resources": [(u'ouicsv', 1, OUI_CSV)]}],
  zipfile = None,
)