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

    Object objects represent a Cloud Files storage object. They must be placed
    inside a Container object.

'''

from hashlib import md5
from helpers import parse_int, DataUsage

class Object(object):
    '''
        A representation of a Cloud Files storage object.
    '''
    
    def __init__(self, name='', file_hash='', bytes=0, content_type='', last_modified=''):
        self._name = name
        self._hash = file_hash
        self._data = DataUsage(bytes)
        self._content_type = content_type
        self._last_modified = last_modified
        self._data = None
        self._stream = None
        self._hash = None
        self._len = 0

    def __repr__(self):
        d = (self.__class__.__name__, self._name, self._data.b, hex(id(self)))
        return '<CloudFiles %s object (%s: %s bytes) at %s>' % d
    
    def __unicode__(self):
        return u'%s' % self.get_name()
    
    def __str__(self):
        return self.get_name()
    
    def get_name(self):
        return self._name
    
    def is_valid(self):
        return True if self._name else False
    
    def set_data(self, data):
        self._data = data
        self._hash = md5(self._data).hexdigest()
        self._len = len(self._data)
    
    def get_data(self):
        return self._data
    
    def set_stream(self, stream, streamlen=0, streamhash=None):
        self._stream = stream
        self._len = streamlen
        if streamhash:
            self._hash = streamhash
    
    def get_stream(self):
        return self._stream
    
    def get_hash(self):
        return self._hash
    
    def get_length(self):
        return self._len
    
    def is_stream(self):
        return True if self._stream else False

'''

    EOF

'''
