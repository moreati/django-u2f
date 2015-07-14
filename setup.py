#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import codecs
import os

from setuptools import setup

with codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'),
                 encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='django-u2f',
    version='0.1',
    description="FIDO U2F security token support for Django",
    long_description=long_description,
    url='https://github.com/gavinwahl/django-u2f',
    packages=[
        'django_u2f',
    ],
    include_package_data=True, # package data will be read from MANIFEST.in
    install_requires=[
        'python-u2flib-server',
        'django',
        'django-otp',
    ],
    author='Gavin Wahl',
    author_email='gavinwahl@gmail.com',
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
    ],
)
