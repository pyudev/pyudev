pyudev -- pure Python libudev_ binding
======================================

pyudev |release| (:doc:`changes`, :doc:`installation <install>`)

pyudev is a :doc:`LGPL licenced <licencing>`, pure Python_ 2/3 binding to
libudev_, the device and hardware management and information library of Linux.

Almost the complete libudev_ functionality is exposed. You can:

* Enumerate devices, filtered by specific criteria (:class:`pyudev.Context`)
* Query device information, properties and attributes,
* Monitor devices, both synchronously and asynchronously with background
  threads, or within the event loops of Qt (:mod:`pyudev.pyqt5`, :mod:`pyudev.pyqt4`,
  :mod:`pyudev.pyside`), glib (:mod:`pyudev.glib`) and wxPython
  (:mod:`pyudev.wx`).


Documentation
-------------

Thanks to the power of libudev_, usage of pyudev is very simple.  Getting the
labels of all partitions just takes a few lines:

>>> import pyudev
>>> context = pyudev.Context()
>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...     print(device.get('ID_FS_LABEL', 'unlabeled partition'))
...
boot
swap
system

A user guide gives an introduction into common operations and concepts of
pyudev, the API documentation provides a detailed reference:

.. toctree::
   :maxdepth: 2

   install
   guide
   api/index


Support
-------

Please report issues, bugs and questions to the `issue tracker`_, but respect
the following guidelines:

- Check that the issue has not already been reported.
- Check that the issue is not already fixed in the ``master`` branch.
- Open issues with clear title and a detailed description in grammatically
  correct, complete sentences.
- Include the Python version and the udev version (see ``udevadm --version``) in
  the description of your issue.


.. _development:

Development
-----------

The source code is hosted on GitHub_::

   git clone https://github.com/lunaryorn/pyudev.git

If you want to contribute to pyudev, please read the guidelines for
contributions and the testsuite documentation.

.. toctree::
   :maxdepth: 2

   contribute
   tests/index


Endorsements
------------
If you're using pyudev and want to say something about it please add yourself
to the endorsements page.

.. toctree::
   :maxdepth: 1

   endorsements


Other reading
-------------

.. toctree::
   :maxdepth: 1

   changes
   licencing


.. _Python: http://www.python.org/
.. _libudev: http://www.freedesktop.org/software/systemd/man/libudev.html
.. _librelist.com: http://librelist.com/
.. _list archives: http://librelist.com/browser/pyudev/
.. _issue tracker: https://github.com/lunaryorn/pyudev/issues
.. _GitHub: https://github.com/lunaryorn/pyudev
