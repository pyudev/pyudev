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

VAGRANT = vagrant
TESTARGS = --enable-privileged -rfEsxX

.PHONY: vagrant-up
vagrant-up:
	$(VAGRANT) up

.PHONY: vagrant-test
vagrant-test: vagrant-up
	$(VAGRANT) ssh -c "cd /vagrant && xvfb-run /home/vagrant/pyudev-py2/bin/py.test $(TESTARGS)"
	$(VAGRANT) ssh -c "cd /vagrant && xvfb-run /home/vagrant/pyudev-py3/bin/py.test $(TESTARGS)"

.PHONY: upload-release
upload-release:
	python setup.py release register sdist upload

pylint:
	pylint pyudev \
		--reports=no \
		--disable=I \
		--disable=bad-continuation \
		--disable=duplicate-code \
		--exclude-protected=_libudev \
		--no-docstring-rgx=_.*

pylint-tests:
	pylint tests \
		--reports=no \
		--disable=I \
		--disable=bad-continuation \
		--disable=duplicate-code \
		--exclude-protected=_libudev \
		--no-docstring-rgx=_.*

PYREVERSE_OPTS = --output=pdf
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=. pyreverse ${PYREVERSE_OPTS} --project="pyudev" pyudev
	mv classes_pyudev.pdf _pyreverse
	mv packages_pyudev.pdf _pyreverse
