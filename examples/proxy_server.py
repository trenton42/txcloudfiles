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

    Start an example server on 0.0.0.0:12345 using the proxy service.

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
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.web import server
from txcloudfiles import get_auth, UK_ENDPOINT, US_ENDPOINT
from txcloudfiles.proxy import get_proxy

def custom_authenticator(method, headers, request_path):
    '''
        Assuming you want to have some form of access control for the proxy
        you can use a custom authenticator. The authenticator is any callable
        that returns a boolean True/False. The arguments are request method
        (such as HEAD, GET) as a str, the request headers as a flat dictionary
        and the request path such as /some/path as a str. You can use this to
        control remote access to the proxy or a simple reauthentication gateway
        to CloudFiles with the proxy handling the CloudFlies API for you.
        
        A typical example would be to check the request headers for basic HTTP
        authentication headers and then returning a True/False.
        
        If False is returned a 401/Unauthorized is returned by the proxy for the
        request automatically.
    '''
    # just for the demo allow global access all the time
    #print 'method:', method
    #print 'headers:', headers
    #print 'request path:', request_path
    return True

username = os.environ.get('TXCFUSR', '')
apikey = os.environ.get('TXCFAPI', '')

# note 'get_proxy' also takes an optional 'servicenet=True' kwarg which tells
# the proxy to authenticate using the rackspace service network.
proxy = get_proxy(UK_ENDPOINT, username, apikey, authenticator=custom_authenticator)

server_endpoint = TCP4ServerEndpoint(reactor, 12345, interface='0.0.0.0')
server_endpoint.listen(proxy)
reactor.run()

'''

    EOF

'''
