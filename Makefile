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

# The default python interpreter used by make
PYTHON ?= python

# pylint settings
PYLINTRC = utils/pylintrc

# sphinx settings
LIBLARCH_DOC_DIR  = docs/liblarch/src
LIBLARCH_GTK_DOC_DIR  = docs/liblarch_gtk/src
DOC_MAKE_FILE    = Makefile-doc
LIBLARCH_DOC_OPTS    = -C $(LIBLARCH_DOC_DIR) -f $(DOC_MAKE_FILE)
LIBLARCH_GTK_DOC_OPTS    = -C $(LIBLARCH_GTK_DOC_DIR) -f $(DOC_MAKE_FILE)
DOC_OPTIONS      = -f -F


.PHONY: clean clean-pyc clean-patchfiles clean-backupfiles doc doc-html \
        clean-generated clean-pylint pylint pylint-report test build develop \
        gen-doc clean-doc

test:
	./run-tests

sdist:
	./build_packages sdist

ppa:
	./build_packages remote-deb

pylint:
	-@pylint --rcfile $(PYLINTRC) liblarch liblarch_gtk

pylint-report:
	-@pylint --rcfile $(PYLINTRC) --output-format=html liblarch > liblarch.html
	-@pylint --rcfile $(PYLINTRC) --output-format=html liblarch_gtk > liblarch_gtk.html

develop:
	@$(PYTHON) setup.py develop

build:
	@$(PYTHON) setup.py build

doc: gen-doc doc-html

gen-doc:
	./bootstrap.py

doc-html:
	$(MAKE) clean html $(LIBLARCH_DOC_OPTS)
	$(MAKE) clean html $(LIBLARCH_GTK_DOC_OPTS)

clean: clean-pyc clean-patchfiles clean-backupfiles clean-generated clean-dist \
       clean-doc clean-pylint

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

clean-doc:
	-@rm -rf $(DOC_OUTPUT_DIR)

clean-pylint:
	-@rm -f liblarch.html
	-@rm -f liblarch_gtk.html
