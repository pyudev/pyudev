# -*- coding: utf-8 -*-
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""
    pyudev.wx
    =========

    Provides :class:`~pyudev.wx.WXUDevMonitorObserver` to integrate a
    :class:`~pyudev.Monitor` into a :meth:`wx.App.MainLoop`.

    To use this module, :mod:`wx` from wxPython must be available.

    .. moduleauthor::  Tobias Eberle  <tobias.eberle@gmx.de>
    .. versionadded:: 0.14
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from threading import Thread

from wx import EvtHandler, PostEvent
from wx.lib.newevent import NewEvent


DeviceEvent, EVT_DEVICE_EVENT = NewEvent()
DeviceAddedEvent, EVT_DEVICE_ADDED = NewEvent()
DeviceRemovedEvent, EVT_DEVICE_REMOVED = NewEvent()
DeviceChangedEvent, EVT_DEVICE_CHANGED = NewEvent()
DeviceMovedEvent, EVT_DEVICE_MOVED = NewEvent()


class WXUDevMonitorObserver(EvtHandler):
    """
    Observe a :class:`~pyudev.Monitor` and posts wx events upon device events:

    >>> context = pyudev.Context()
    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = pyudev.wx.WXUDevMonitorObserver(monitor)
    >>> def device_connected(event):
    ...     print('{0!r} added'.format(event.device))
    >>> observer.Bind(EVT_DEVICE_ADDED, device_connected)
    >>> ...
    >>> observer.stop() # because otherwise only the MainLoop exits, but not
    >>>                 # the python interpreter

    This class is a child of :class:`wx.EvtHandler`.
    """

    _action_event_map = {
        'add': DeviceAddedEvent,
        'remove': DeviceRemovedEvent,
        'change': DeviceChangedEvent,
        'move': DeviceMovedEvent
    }

    def __init__(self, monitor):
        EvtHandler.__init__(self)
        self.monitor = monitor
        self._thread = Thread(target=self._observe_monitor)
        self._thread.start()

    def stop(self):
        """
        stops observing the monitor

        It is neccessary to run this when the wxwidgets application exits to
        also allow the python interpreter to exit. Otherwise the python
        interpreter keeps running.
        """
        self._thread._Thread__stop()

    def _observe_monitor(self):
        for event in self.monitor:
            action, device = event
            PostEvent(self, DeviceEvent(action=action, device=device))
            event_class = self._action_event_map[action]
            PostEvent(self, event_class(device=device))

