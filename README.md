txcloudfiles
============

txcloudfiles is a Python+Twisted interface to Rackspace Cloud Files using the
Cloud Files API v1.0 over JSON. The API documentation can be found here:

http://docs.rackspace.com/files/api/v1/cf-devguide/content/index.html

This library is feature-complete at time of release, please see the /examples/
folder for detailed bare examples on all operations. It also supports streaming
of files via producers for efficient uploading and downloading of large files.

All operations are fully asynchronous and will be simple to anyone who is
familiar with Twisted.

txcloudfiles was Developed and tested with Python 2.7 and Twisted 11.1, although
it should work given the features used (but not tested) with Python >= 2.6 and
Twisted >= 9.0.

You can install (and use --upgrade to upgrade) the latest version via "pip"
directly from github:

```bash
$ pip install git+git://github.com/meeb/txcloudfiles.git@master
```

Please do report, fork or otherwise notify me of any bugs or issues.
