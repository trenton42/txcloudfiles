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

    Account objects represent a Cloud Files account. Stores meta-data relating
    to account operations.

'''

from helpers import parse_int, DataUsage
from errors import RequestException

class Account(object):
    '''
        A representation of a Cloud Files account.
    '''
    
    def __init__(self, username=''):
        self._username = username
        self._container_count = 0
        self._data_used = None
    
    def __repr__(self):
        return '<CloudFiles %s object (%s) at %s>' % (self.__class__.__name__, self._username, hex(id(self)))
    
    def set_container_count(self, x):
        self._container_count = parse_int(x)
    
    def set_bytes_used(self, x):
        self._data_used = DataUsage(x)
    
    def get_container_count(self):
        return self._container_count
    
    def get_data_used(self, bandwidth=DataUsage.BANDWIDTH_B):
        return self._data_used.get_in(bandwidth)

'''

    EOF

'''
