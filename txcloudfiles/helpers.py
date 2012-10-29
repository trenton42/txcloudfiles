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

    Some helper functions and classes.

'''

from urllib import quote_plus
from errors import CloudFilesException

def parse_int(x):
    try:
        return int(x)
    except ValueError:
        return 0

def parse_str(x):
    try:
        return str(x)
    except ValueError:
        return ''

def parse_url_str(x):
    return quote_plus(parse_str(x))[:256]

class Metadata(object):
    
    ACCOUNT = 'X-'
    CONTAINER = 'X-Container-Meta-'
    OBJECT = 'X-Object-Meta-'
    CDN = 'X-'
    DEFAULT = 'X-Meta-'
    
    def __init__(self, prefix=None):
        self.prefix = self.OBJECT if prefix == self.OBJECT else self.CONTAINER
    
    def is_metadata_header(self, header):
        return header.title()[:len(self.prefix)] == self.prefix
    
    def prefix_header(self, header):
        header = header.title()
        if not self.is_metadata_header(header):
            return self.prefix + header
        return header
    
    def parse_header(self, header):
        header = header.title()
        if self.is_metadata_header(header):
            return header[len(self.prefix):].lower()
        return header
    
    def loads(self, headers):
        meta_headers = {}
        for k,v in headers.items():
            if self.is_metadata_header(k):
                meta_headers[self.parse_header(k)] = v
        return meta_headers
    
    def dumps(self, headers):
        for k,v in headers.items():
            headers[self.prefix_header(k)] = v
        return headers
    
    def to_remote(self, header):
        '''
            Changes generic X-Meta- headers into X-Meta-[context specific]-
            headers.
        '''
        if header.title()[:len(self.DEFAULT)] == self.DEFAULT:
            return self.prefix + header.title()[len(self.DEFAULT)+1:]
    
    def from_remote(self, header):
        '''
            Changes remote X-Meta-[context specific]- headers into generic
            X-Meta- headers.
        '''
        if header.title()[:len(self.prefix)] == self.prefix:
            return self.DEFAULT + header.title()[len(self.prefix)+1:]

class DataUsage(object):
    
    BANDWIDTH_B = 1
    BANDWIDTH_KB = 1024
    BANDWIDTH_MB = 1024*1024
    BANDWIDTH_GB = 1024*1024*1024
    BANDWIDTH_TB = 1024*1024*1024*1024
    BANDWIDTH_PB = 1024*1024*1024*1024*1024
    BANDWIDTHS = (
        BANDWIDTH_B,
        BANDWIDTH_KB,
        BANDWIDTH_MB,
        BANDWIDTH_GB,
        BANDWIDTH_TB,
        BANDWIDTH_PB,
    )
    
    def __init__(self, bytes=0):
        self._bytes = parse_int(bytes)
        self.b = self.get_in(self.BANDWIDTH_B)
        self.kb = self.get_in(self.BANDWIDTH_KB)
        self.mb = self.get_in(self.BANDWIDTH_MB)
        self.gb = self.get_in(self.BANDWIDTH_GB)
        self.tb = self.get_in(self.BANDWIDTH_TB)
    
    def get_in(self, bandwidth=0):
        if bandwidth not in self.BANDWIDTHS:
            raise CloudFilesException('invalid bandwidth format specified: %s' % bandwidth)
        if bandwidth == 1:
            return float(self._bytes)
        return round((float(self._bytes) / float(bandwidth)), 5)

'''

    EOF

'''
