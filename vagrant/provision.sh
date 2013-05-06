#!/bin/sh
# Copyright (C) 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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

apt_update () {
    sudo apt-get update -qq
}

apt () {
    sudo apt-get install -yy --fix-missing "$@"
}

make_pyudev_venv () {
  rm -rf "/home/vagrant/$2"
  virtualenv -qq -p "$1" --system-site-packages "/home/vagrant/$2"
  . "/home/vagrant/$2/bin/activate"
  pip install -q -i https://restricted.crate.io/ -r "/vagrant/requirements.txt"
  pip install -q -e /vagrant
  deactivate
}

# Silence debconf
export DEBIAN_FRONTEND='noninteractive'

apt_update

echo "Installing basic packages"
apt unzip make git \
  python python-pip python-virtualenv \
  python3

echo "Installing Tox for Venv management"
sudo pip install -q -i https://restricted.crate.io/ -U tox

echo "Installing headers for coverage tests"
apt libudev-dev gccxml

echo "Installing supported GUI toolkits"
apt python-qt4 python3-pyqt4 \
  python-pyside python3-pyside \
  python-wxgtk2.8 xvfb \
  python-gobject

echo "Creating test virtualenvs"
make_pyudev_venv python2 pyudev-py2
make_pyudev_venv python3 pyudev-py3
