#
# Cookbook Name:: pyudev
# Recipe:: virtualenv
#
# Copyright (C) 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
#

# Create a virtualenv for testing

if node[:instance_role] == "vagrant"
  # Only create the virtualenv on a vagrant machine

  # FIXME: extract user name from vagrant configuration
  username = "vagrant"
  virtualenv = "/home/#{username}/pyudev-env"

  # Delete any existing environments
  directory virtualenv do
    action :delete
    recursive true
  end

  # Setup the new environment
  python_virtualenv virtualenv do
    owner username
    group username
    # We need system packages to include native bindings
    options "--system-site-packages"
    action :create
  end

  # Install test runner
  python_pip "pytest" do
    virtualenv virtualenv
    action :install
  end

  # Install dependencies of tests (docutils is required by PyPI tests)
  python_pip "mock" do
    virtualenv virtualenv
    action :install
  end

  python_pip "docutils" do
    virtualenv virtualenv
    action :install
  end

  # Install pyudev into virtualenv
  python_pip "/vagrant" do
    virtualenv virtualenv
    action :install
    options "-e"
  end
end
