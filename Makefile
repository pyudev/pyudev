# Copyright (C) 2012, 2013 Sebastian Wiesner <lunaryorn@gmail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

package:
	(umask 0022; python -m build; python -m twine check --strict ./dist/*)

lint:
	pylint setup.py
	pylint src/pyudev/_os/poll.py
	pylint src/pyudev/_compat.py

PYREVERSE_OPTS = --output=pdf
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="pyudev" src/pyudev
	mv classes_pyudev.pdf _pyreverse
	mv packages_pyudev.pdf _pyreverse

archive:
	git archive --output=./archive.tar.gz HEAD

.PHONY: test-travis
test-travis:
	py.test --junitxml=tests.xml  -rfEsxX

.PHONY: fmt
fmt:
	isort setup.py src tests
	black .

.PHONY: fmt-travis
fmt-travis:
	isort --diff --check-only setup.py src tests
	black . --check

.PHONY: yamllint
yamllint:
	yamllint --strict .github/workflows/*.yml
