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

    Trivial example of how to set an account temporary URL key. See:
    
    http://docs.rackspace.com/files/api/v1/cf-devguide/content/Set_Account_Metadata-d1a4460.html

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

from hashlib import sha256
from twisted.internet import reactor
from txcloudfiles import get_auth, UK_ENDPOINT, US_ENDPOINT

def _got_session(session):
    print '> got session: %s' % session
    random_key = sha256(os.urandom(256)).hexdigest()
    def _ok(v):
        # 'v' is just a boolean True, if there was an error errback() would
        # have been fired
        print '> set temp url key to:'
        print random_key
        reactor.stop()
    session.set_temp_url_key(random_key).addCallback(_ok).addErrback(_error)

def _error(e):
    print 'error'
    print e
    reactor.stop()

auth = get_auth(UK_ENDPOINT, os.environ.get('TXCFUSR', ''), os.environ.get('TXCFAPI', ''))
auth.get_session().addCallback(_got_session).addErrback(_error)

reactor.run()

'''

    EOF

'''
