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

    A session is a self-verifying authentication storage object as well as
    containing top level request wrappers to construct Account() and Container()
    objects.

'''

from time import time
from urlparse import urlsplit
from twisted.internet.defer import Deferred
from errors import NotAuthenticatedException, RequestException
from operations.account import AccountRequest
from cfaccount import Account

class Session(object):
    '''
        Holds a single authentication session.
    '''
    
    # while the documentation says authtokens are valid for 24h
    # set it to 12h so it can't ever expire
    AUTH_TIMELIMIT = 5
    
    def __init__(self, username='', key='', storage_url='', management_url='', servicenet=''):
        self._timer = time() if key else 0
        self._username = username if username else ''
        self._key = key if key else ''
        self._storage_url = storage_url
        self._management_url = management_url
        self._storage_url_parts = urlsplit(storage_url)
        self._management_url_parts = urlsplit(management_url)
        self._servicenet = ''
    
    def _is_valid(self):
        if self._timer == 0 or not self._key:
            raise NotAuthenticatedException('token not set')
        elif self._timer < time() - self.AUTH_TIMELIMIT:
            raise NotAuthenticatedException('token has expired')
        return True
        
    def is_valid(self):
        try:
            valid = self._is_valid()
        except NotAuthenticatedException:
            valid = False
        return valid
    
    def get_key(self):
        if self.is_valid():
            return self._key
        return ''
    
    def get_storage_url_parts(self):
        if self._servicenet:
            self._storage_url_parts.netloc = self._servicenet + self._storage_url_parts.netloc
        return self._storage_url_parts
    
    def get_management_url_parts(self):
        return self._management_url_parts
    
    ''' account wrappers '''
    
    def get_account(self):
        d = Deferred()
        
        def _parse(r):
            if r.OK:
                a = Account()
                a.set_container_count(r.headers.get('X-Account-Container-Count', ''))
                a.set_bytes_used(r.headers.get('X-Account-Bytes-Used', ''))
                d.callback(a)
            elif r.status_code == 401:
                d.errback(NotAuthenticatedException('failed to get account information, not authorised'))
            else:
                d.errback(RequestException('failed to get account information'))
        
        request = AccountRequest(self)
        request.set_parser(_parse)
        request.run()
        return d

'''

    EOF

'''
