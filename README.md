txcloudfiles
============

txcloudfiles is a Python Twisted interface to rackspace cloud files using the
cloudfiles API v1.0 and JSON. API documentation can be found here:

http://docs.rackspace.com/files/api/v1/cf-devguide/content/index.html

As this is currently under development it should not be used.

Developed and tested with Python 2.7 and Twisted 11.1, it is not advised to
attempt to use earlier versions of Python or Twisted (given txcloudfiles uses
the standard json module it will certainly fail with Python < 2.6).
