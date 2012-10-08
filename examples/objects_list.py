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

    Trivial example of how to list all objects in a container. See:
    
    http://docs.rackspace.com/files/api/v1/cf-devguide/content/Serialized_List_Output-d1e1460.html

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
from txcloudfiles import get_auth, UK_ENDPOINT, US_ENDPOINT

def _got_session1(session):
    print '> got session 1: %s' % session
    def _ok((response, containerset)):
        '''
            'containerset' is a cfcontainer.ContainerSet() instance.
        '''
        print '> got containerset: %s' % containerset
        if len(containerset) > 0:
            first_container = containerset[0]
            print '> listing objects in first container in containerset: %s' % first_container
            # requesting a second session is not required here as sessions
            # can last for a day or so, however, as auth.get_session() returns
            # the same valid session again this doesn't slow anything down and
            # is generally good practice to avoid accidentally using a session
            # until it expires.
            auth.get_session().addCallback(_got_session2, first_container).addErrback(_error)
        else:
            print '! no containers on account'
    session.list_containers().addCallback(_ok).addErrback(_error)

def _got_session2(session, first_container):
    print '> got session 2: %s' % session
    def _ok((response, container)):
        '''
            'response' is a transport.Response() instance.
            'container' is a cfcontainer.Container() instance.
        '''
        print '> got response: %s' % response
        print '> got container populated with objects: %s' % container
        for obj in container:
            print obj, repr(obj)
        reactor.stop()
    print '> sending request'
    session.list_objects(first_container).addCallback(_ok).addErrback(_error)

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
auth.get_session().addCallback(_got_session1).addErrback(_error)

reactor.run()

'''

    EOF

'''
