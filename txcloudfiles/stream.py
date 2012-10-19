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

    Stream classes are protocol handlers used for upstream and downstream
    streaming to and from HTTP servers.

'''

from twisted.internet.protocol import Protocol

class DownstreamTransportProtocol(Protocol):
    '''
        Handle downloading/streaming of data from HTTP servers.
    '''
    
    def __init__(self, d, streamclient=None):
        self.d = d
        self.streamclient = streamclient
        self.buffer = ''
    
    def dataReceived(self, data):
        if self.streamclient:
            pass
        else:
            self.buffer += data
    
    def connectionLost(self, reason):
        if self.streamclient:
            pass
        else:
            self.d.callback(self.buffer)

'''

    EOF

'''
