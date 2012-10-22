txcloudfiles
============

*This package is still under heavy active development, is missing features and*
*generally should not be used until this notice has been removed.*

txcloudfiles is a Python Twisted interface to rackspace cloud files using the
cloudfiles API v1.0 and JSON. API documentation can be found here:

http://docs.rackspace.com/files/api/v1/cf-devguide/content/index.html

Once out of beta this package will aim to be a feature-complete twisted library
for accessing Cloud Files.

Developed and tested with Python 2.7 and Twisted 11.1, it is not advised to
attempt to use earlier versions of Python or Twisted (given txcloudfiles uses
the standard json module it will certainly fail with Python < 2.6).

Todo:
 * add large object streaming support
 * general code check

