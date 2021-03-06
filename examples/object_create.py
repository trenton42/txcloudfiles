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

    Trivial example of how to create an object without streaming. Complete file
    contents is buffered. Only usable for small files. See:
    
    http://docs.rackspace.com/files/api/v1/cf-devguide/content/Create_Update_Object-d1e1965.html

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

from twisted.internet import reactor
from txcloudfiles.cfobject import Object
from txcloudfiles import get_auth, UK_ENDPOINT, US_ENDPOINT

def _got_session(session):
    print '> got session: %s' % session
    container_name = 'some_test_container'
    object_instance = Object('some_test_object.txt')
    object_instance.set_content_type('text/plain')
    object_instance.set_compressed()
    object_instance.set_data('example data in object')
    def _ok((response, obj)):
        '''
            'response' is a transport.Response() instance.
            'obj' is a cfobject.Object() instance.
        '''
        print '> got response: %s' % response
        print '> created object: %s/%s' % (container_name, object_instance.get_name())
        print '> got object populated with response data: %s' % obj
        reactor.stop()
    print '> sending request'
    # create_object() also takes an optional 'delete_at' kwarg which if set to a
    # datetime.datetime instance in the future will reques the object be deleted
    # from the rackspace cloudfiles servers at that time, use timedelta's to
    # specify rolling timers (e.g. delete this 24hr's from now).
    session.create_object(container_name, object_instance).addCallback(_ok).addErrback(_error)

def _error(e):
    '''
        'e' here will be a twisted.python.failure.Failure() instance wrapping
        a ResponseError() object. ResponseError() instances contain information
        about the request to help you find out why it errored through its 
        ResponseError().request attribute.
    '''
    print 'error!'
    print e.printTraceback()
    reactor.stop()

auth = get_auth(UK_ENDPOINT, os.environ.get('TXCFUSR', ''), os.environ.get('TXCFAPI', ''))
auth.get_session().addCallback(_got_session).addErrback(_error)

reactor.run()

'''

    EOF

'''
