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

    Trivial example of how to upload an object via streaming. This code will
    connect to the server started by 'stream_upload_server.py'. Note as this
    is being translated into HTTP you need to know the size of the stream
    before you upload it (preferably as well as the md5 hash so we can confirm
    the upload was a success). This is meant for uploading large local files
    where finding out the existing md5 hash and file size before starting the
    upload is not an issue. It is not suitable for streaming data of unknown
    length (e.g. an audio stream) as the Content-Length must be set to store it
    over HTTP.

'''

from hashlib import md5
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

def pack_header(length, name, container, mimetype, md5hash):
    # pack a simplistic header, each value is in plain text and padded to 32
    # bytes in length, unpacked by the example server to tell the cloud files
    # server how long our stream is going to be etc.
    d = str(length)[:32].ljust(32)
    d += name[:32].ljust(32)
    d += container[:32].ljust(32)
    d += mimetype[:32].ljust(32)
    d += md5hash[:32].ljust(32)
    return d

class StreamingClientProtocol(Protocol):
    '''
        Connect to the simple server on loopback and spam our test data into it.
        This would usuallly be a remote client, this is connecting to loopback
        just as an example.
    '''
    
    # container name, static for example client
    CONTAINER_NAME = 'some_test_container'
    # object name, static for example client
    OBJECT_NAME = 'some_test_object.txt'
    # exactly one MB of exlamation marks as our test data ...
    EXAMPLE_DATA = b'\x21' * (1024 * 1024)
    # ... which is exactly 1MB in size
    EXAMPLE_DATA_SIZE = 1024 * 1024
    # and a data type for our example data
    DATA_TYPE = 'text/plain'
    
    def connectionMade(self):
        # first write a minimal header, 32 byte plain text values padded with spaces
        header = pack_header(
            self.EXAMPLE_DATA_SIZE,
            self.OBJECT_NAME,
            self.CONTAINER_NAME,
            self.DATA_TYPE,
            md5(self.EXAMPLE_DATA).hexdigest()
        )
        print 'sending header...'
        self.transport.write(header)
        # write our data in 128 byte chunks to simulate a stream
        chunk_size = 128
        for i in xrange(self.EXAMPLE_DATA_SIZE / chunk_size):
            chunk = i * chunk_size
            chunk_data = self.EXAMPLE_DATA[chunk:chunk+chunk_size]
            print 'sending chunk of length:', len(chunk_data)
            self.transport.write(chunk_data)
        # usually you would want to write back some verification from the server
        # here but just disconnect as it's a hacky example
        print 'all done, dropping connection...'
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        reactor.stop()
    
client_factory = Factory()
client_factory.protocol = StreamingClientProtocol
client_endpoint = TCP4ClientEndpoint(reactor, '127.0.0.1', 12345)
client_endpoint.connect(client_factory)

reactor.run()

'''

    EOF

'''
