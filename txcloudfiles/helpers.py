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

class Metadata(object):
    
    PREFIX = 'X-Container-Meta-'
    
    def is_metadata_header(self, header):
        return k.title()[:len(self.PREFIX)] == self.PREFIX
    
    def loads(self, headers):
        for k,v in headers.items():
            k = k.replace(self.PREFIX, '')
            headers[k] = v
        return v
    
    def dumps(self, headers):
        for k,v in headers.items():
            k = k.title()
            if self.is_metadata_header(k):
                k = self.PREFIX + k
            headers[k] = v
        return v

class DataUsage(object):
    
    BANDWIDTH_B = 1
    BANDWIDTH_KB = 1024
    BANDWIDTH_MB = 1024*1024
    BANDWIDTH_GB = 1024*1024*1024
    BANDWIDTH_TB = 1024*1024*1024*1024
    BANDWIDTHS = (
        BANDWIDTH_B,
        BANDWIDTH_KB,
        BANDWIDTH_MB,
        BANDWIDTH_GB,
        BANDWIDTH_TB,
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
