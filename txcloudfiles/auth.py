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

    Authentication instances store the required connection information for
    handshaking with the remote authentication service, including caching
    of authentication tokens.

'''

from twisted.internet import task
from twisted.internet.defer import Deferred
from requests.auth import AuthRequest
from session import Session
from errors import InvalidEndpointException, CannotCreateSessionException

class Endpoint(object):
    '''
        Static constants used to configure the which endpoint a session is
        connecting to.
    '''
    ENDPOINT_VERSION = 'v1.0'
    ENDPOINT_SCHEME = 'https'
    UK_ENDPOINT = 'lon.auth.api.rackspacecloud.com'
    US_ENDPOINT = 'auth.api.rackspacecloud.com'
    SNET_PREFIX = 'snet-'
    ENDPOINTS = (
        UK_ENDPOINT,
        US_ENDPOINT
    )
    # aliases
    UK = UK_ENDPOINT
    US = US_ENDPOINT
    
    def __init__(self, endpoint, servicenet=False):
        if endpoint not in Endpoint.ENDPOINTS:
            raise InvalidEndpointException('supplied endpoint is invalid: %s' % endpoint)
        self.endpoint = endpoint
        self.servicenet = True if servicenet else False
    
    def get_endpoint(self):
        return self.endpoint
    
    def get_version(self):
        return self.ENDPOINT_VERSION
    
    def get_scheme(self):
        return self.ENDPOINT_SCHEME
    
    def get_auth_url(self):
        return '%(scheme)s://%(netloc)s/%(version)s' % {
            'scheme': self.get_scheme(),
            'netloc': self.get_endpoint(),
            'version': self.get_version(),
        }

class BaseAuth(object):
    '''
        Root authentication class with other authentication classes inherit.
    '''
    
    QUEUE_LOOP_TIMER = 1.0
    
    def __init__(self, endpoint=None, username='', apikey='', **kwargs):
        if not isinstance(endpoint, Endpoint):
            raise InvalidEndpointException('supplied endpoint is invalid: %s' % endpoint)
        self._endpoint = endpoint
        self._username = username
        self._apikey = apikey
        self._endpoint = endpoint
        self._options = kwargs
        self._session = None
        self._session_queue = []
        self._waiting = False
        self._queue_loop = task.LoopingCall(self._process_queue)
    
    def _get_apikey(self):
        return self._apikey
    
    def get_endpoint(self):
        return self._endpoint
    
    def get_username(self):
        return self._username
    
    def use_servicenet(self):
        return self._endpoint.servicenet
    
    def _get_session(self):
        if self._session and self._session.is_valid():
            return self._session
        self._session = None
        return None
    
    def _set_session(self, session):
        self._session = session
    
    def _session_is_valid(self):
        return self._session and self._session.is_valid()
    
    def is_valid(self):
        try:
            self._get_token()
        except NotAuthenticatedException:
            return False
        return True
    
    def _queue_request(self, d):
        self._session_queue.append(d)
    
    def _process_queue(self):
        if not self._session_queue or not self._session_is_valid() or self._waiting:
            return
        session = self._get_session()
        while True:
            try:
                d = self._session_queue.pop()
                d.callback(d)
            except IndexError:
                break
    
    def start_queue(self):
        if not self._queue_loop.running:
            self._queue_loop.start(self.QUEUE_LOOP_TIMER)
    
    def stop_queue(self):
        if self._queue_loop.running:
            self._queue_loop.stop()

class Auth(BaseAuth):
    '''
        An authentication implementation which automatically refreshes the auth
        token if it expires. Extends BaseAuth to provide token aquisition
        from the Cloud Files authentication service.
    '''
    
    def get_session(self):
        '''
            Returns a deferred which when fired returns an account object or
            an authentication error. Any extra arguments given are passed back
            when the callback is fired.
        '''
        self.start_queue()
        d = Deferred()
        
        def _parse(r):
            self._waiting = False
            if r.OK:
                self._set_session(Session(
                    username=self.get_username(),
                    key=r.headers.get('X-Auth-Token', ''),
                    storage_url=r.headers.get('X-Storage-Url', ''),
                    cdn_url=r.headers.get('X-Cdn-Management-Url', ''),
                    servicenet=Endpoint.SNET_PREFIX if self.use_servicenet() else ''
                ))
                # send the session off to the callback
                d.callback(self._get_session())
            else:
                e = 'authorisation error' if r.status_code == 401 else 'transport error'
                d.errback(CannotCreateSessionException('error creating session: %s' % e))
        
        # if we already have a valid session fire it back immedaitely
        if self._session_is_valid():
            d.callback(self._get_session())
        # if we're already waiting for a new session pop it into the session
        # request queue
        elif self._waiting:
            self._queue_request(d)
        # if not, attempt to request a new session
        else:
            request = AuthRequest(self)
            request.set_header(('X-Auth-User', self.get_username()))
            request.set_header(('X-Auth-Key', self._get_apikey()))
            request.set_parser(_parse)
            self._waiting = True
            request.run()
        return d

def get_auth(endpoint, username, apikey):
    '''
        Wrapper for the above classes.
    '''
    return Auth(Endpoint(endpoint), username, apikey)

'''

    EOF

'''
