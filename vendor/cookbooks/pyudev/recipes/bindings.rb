#
# Cookbook Name:: pyudev
# Recipe:: bindings
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


apt_repository "pyside-official" do
  uri "http://ppa.launchpad.net/pyside/ppa/ubuntu"
  distribution node['lsb']['codename']
  components ["main"]
  keyserver "keyserver.ubuntu.com"
  key "073700C1"
  deb_src true
end

# Install supported bindings
package "python-qt4" do
  action :install
end

package "python-pyside" do
  action :install
end

package "python-wxgtk2.8" do
  action :install
end

# wxPython needs a X11 display to be used, hence install xvfb to provide a fake
# X11 display
package "xvfb" do
  action :install
end

package "python-gobject" do
  action :install
end
