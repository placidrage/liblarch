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

# Simple makefile for common tasks

PYTHON ?= python

.PHONY: clean clean-pyc clean-patchfiles clean-backupfiles \
        clean-generated clean-pylint pylint pylint-report test build develop

test:
	./run-tests

sdist:
	./build_packages sdist

ppa:
	./build_packages remote-deb

pylint:
	-@pylint --rcfile pylintrc liblarch liblarch_gtk

pylint-report:
	-@pylint --rcfile pylintrc --output-format=html liblarch > liblarch.html
	-@pylint --rcfile pylintrc --output-format=html liblarch_gtk > liblarch_gtk.html

build:
	@$(PYTHON) setup.py build

develop:
	@$(PYTHON) setup.py develop

clean: clean-pyc clean-patchfiles clean-backupfiles clean-generated clean-dist \
       clean-pylint

# Remove .py[c,o] files
clean-pyc:
	-@find . -type f -iname '*.pyc' -exec rm -f {} +
	-@find . -type f -iname '*.pyo' -exec rm -f {} +

clean-patchfiles:
	-@find . -name '*.orig' -exec rm -f {} +
	-@find . -name '*.rej' -exec rm -f {} +

clean-backupfiles:
	-@find . -name '*~' -exec rm -f {} +
	-@find . -type f -iname '*.bak' -exec rm -f {} +

clean-dist:
	-@rm -rf dist/

clean-pylint:
	-@rm -f liblarch.html
	-@rm -f liblarch_gtk.html
