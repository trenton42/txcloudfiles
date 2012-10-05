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

    A session is a self-verifying interface to the top level requests to the
    API, such as account data and container information.

'''

from time import time
from errors import NotAuthenticatedException

class Session(object):
    '''
        An authentication session containing a authentication key on a timer.
        Contains wrapper functions to access the top level account data.
    '''
    
    # while the documentation says authtokens are valid for 24h
    # set it to 12h so it can't ever expire
    AUTH_TIMELIMIT = 5
    
    def __init__(self, key='', storage_url='', management_url='', servicenet=False):
        self._timer = time() if key else 0
        self._key = key if key else ''
        self._servicenet = servicenet
    
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
        return False

'''

    EOF

'''
