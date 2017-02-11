#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
from codecs import open
import sys
import os
import re
import oui

def get_version(path):
    with open(path, encoding='utf-8') as f:
        version_file = f.read()
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_match = re.search(regex, version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string in %s.', version_file)

with open('LICENSE', encoding='utf-8') as f:
    license = f.read()

    
setup(
    name='oui',
    version=get_version('oui/_version.py'),
    description='oui tool finds MAC address vendor and displays it in multiple common formats',
    author='Mick Shine',
    author_email='madmixtar@gmail.com',
    url='https://github.com/madmickstar/oui',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['pypiwin32 >= 219'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
)