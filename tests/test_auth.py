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

import os, sys
from twisted.trial import unittest

# make sure our local copy of txcloudfiles is in sys.path
PATH_TO_TXCF = '../txcloudfiles/'
try:
    import txcloudfiles
except ImportError:
    txcfpath = os.path.dirname(os.path.realpath(PATH_TO_TXCF))
    if txcfpath not in sys.path:
        sys.path.insert(0, txcfpath)

from txcloudfiles.auth import Endpoint, Auth

class AuthTest(unittest.TestCase):
    '''
        Validate the authentication operations.
    '''
    
    def test_endpoints(self):
        '''
            Verify Endpoint() accepts the required endpoints
        ''' 
        for endpoint in ('lon.auth.api.rackspacecloud.com', 'auth.api.rackspacecloud.com'):
            e = Endpoint(endpoint)
            self.assert_(e.get_endpoint() == endpoint, 'invalid endpoint returned: %s' % endpoint)
            u = 'https://%s/v1.0' % endpoint
            self.assert_(e.get_auth_url() == u, 'invalid endpoint url returned: %s' % e.get_auth_url())
        del e, u
    
    def test_auth(self):
        '''
            Verify an Auth() can be constructed properly, check it stored our
            authentication details properly.
        '''
        e = Endpoint(Endpoint.UK)
        a = Auth(e, self.usr, self.key)
        self.assert_(a.get_username() == self.usr, 'Session() did not store username')
        self.assert_(a.get_endpoint() == e, 'Session() did not store the Endpoint()')
        a.stop_queue()
        del e,a
    
    def test_remote_auth(self):
        '''
            Verify a Auth().get_session() returns a valid Session.
        '''
        def _got_data(s):
            self.assert_(s.is_valid(), 'unable to request remote auth token')
        def _got_error(e):
            print e
            self.fail(e)
        e = Endpoint(Endpoint.UK)
        a = Auth(e, self.usr, self.key)
        d = a.get_session()
        d.addCallback(_got_data)
        d.addErrback(_got_error)
        a.stop_queue()
        return d
    
    def setUp(self):
        self.usr = os.environ.get('TXCFUSR', '')
        self.key = os.environ.get('TXCFAPI', '')
    
    def tearDown(self):
        del self.usr
        del self.key

'''

    EOF

'''
