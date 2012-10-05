#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

    Copyright 2012 Joe Harris

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''

'''

    Trivial example of how to request Cloud Files account meta data.

'''

import os, sys

# make sure our local copy of txcloudfiles is in sys.path
PATH_TO_TXCF = '../txcloudfiles/'
try:
    import txcloudfiles
except ImportError:
    txcfpath = os.path.dirname(os.path.realpath(PATH_TO_TXCF))
    if txcfpath not in sys.path:
        sys.path.insert(0, txcfpath)

from twisted.internet import reactor, defer
from txcloudfiles import Endpoint, Auth, DataUsage

def _d(session):
    print '> got session'
    def _got_account(account):
        print '> got account'
        print 'number of containers:', account.get_container_count()
        print 'megabytes used:', account.get_data_used(DataUsage.BANDWIDTH_MB)
        reactor.stop()
    session.get_account().addCallback(_got_account).addErrback(_e)

def _e(e):
    print 'error'
    print e
    reactor.stop()

e = Endpoint(Endpoint.UK)
a = Auth(e, 'depeer1', 'd3d855500220a2bf7c7df3973c5b7b0a')
a.get_session().addCallback(_d).addErrback(_e)

reactor.run()

'''

    EOF

'''
