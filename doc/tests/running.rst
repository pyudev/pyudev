Test running
============
See the current CI configuration file to determine what tests are
currently being run and how to run them.

Device samples
~~~~~~~~~~~~~~

Many pyudev tests run against the real device database of the system the tests
are executed on.  As testing against the whole database takes a long time,
tests are run against a random sample by default.  With the command line
options provided by :mod:`~tests.plugins.udev_database` you can configure the
size of this sample, or run the tests against a single device or the whole
database.
