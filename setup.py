#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Liblarch - a library to handle directed acyclic graphs
# Copyright (c) 2011-2012 - Lionel Dricot & Izidor Matušov
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import sys
import liblarch


# -----------------------------------------------------------------------------

if sys.version_info < (2, 7):
    print('ERROR: liblarch requires at least Python 2.7 to run.')
    sys.exit(1)

# -----------------------------------------------------------------------------

params = {}
params['liblarch'] = {
    'description': (
        'Liblarch is a python library built to easily handle '
        'data structure such are lists, trees and acyclic graphs (tree where '
        'nodes can have multiple parents)'),
}

params['liblarch_gtk'] = {
    'description': 'GTK binding for Liblarch.',
}

# -----------------------------------------------------------------------------

standalone_packages = find_packages(exclude=['tests'])

for package in standalone_packages:
    pkg_version = liblarch.__version__

    setup(
      version = pkg_version,
      url = 'https://live.gnome.org/liblarch',
      author = 'Lionel Dricot & Izidor Matušov',
      author_email = 'gtg-contributors@lists.launchpad.net',
      license = 'LGPLv3',
      name = package,
      packages = [package],
      command_options={
          'build_sphinx': {
              'project': ('setup.py', package),
              'version': ('setup.py', pkg_version),
              'release': ('setup.py', pkg_version),
          }
      },
      **params[package]
    )

# -----------------------------------------------------------------------------
