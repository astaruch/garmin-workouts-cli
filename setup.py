# -*- coding: utf-8 -*-
"""
    Garmin Workouts CLI is a command line application allowing you to work
    with Garmin Connect Workouts through the command line in sane matter.
    :copyright: (c) 2020 by Andrej Staruch.
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'garmin_workouts/version.py'), 'r') as f:
    version = f.read().strip()

with open(join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

with open(join(dirname(__file__), 'README.rst'), 'r') as f:
    long_description = f.read()

setup(
    name='garmin-workouts-cli',
    version=version,
    description="Command line application to work with Garmin Connect Workouts",
    long_description=long_description,
    url='https://github.com/astaruch/garmin-workouts-cli',
    author='Andrej Staruch',
    author_email='staruch.andrej@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='garmin, connect, workouts, triathlon, run, calendar   ',
    packages=['garmin_workouts'],
    python_requires='>=3.5, <4',
    install_requires=install_requires,
)
