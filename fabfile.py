#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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


from fabric.api import task, env, local, cd, run, execute


def get_vagrant_ssh_config():
    config = {}
    for line in local('vagrant ssh-config', capture=True).splitlines():
        line = line.strip()
        key, value = line.split(' ', 1)
        config[key] = value
    return config


@task
def vagrant_up():
    local('vagrant up')
    config = get_vagrant_ssh_config()
    env.key_filename = config['IdentityFile']
    env.hosts = ['{User}@{HostName}:{Port}'.format(**config)]
    env.reject_unknown_hosts = False


@task
def vagrant_virtualenv():
    with cd('$HOME'):
        run('virtualenv pyudev')
    with cd('/vagrant'):
        run('$HOME/pyudev/bin/pip install -e .')
        run('$HOME/pyudev/bin/pip install -r requirements.txt')


@task
def vagrant_run_tests(verbose='no'):
    with cd('/vagrant'):
        cmd = '$HOME/pyudev/bin/py.test -rs --enable-privileged'
        if verbose == 'yes':
            cmd += ' --verbose'
        run(cmd)


@task
def test(verbose='no'):
    execute(vagrant_up)
    execute(vagrant_virtualenv)
    execute(vagrant_run_tests, verbose=verbose)
