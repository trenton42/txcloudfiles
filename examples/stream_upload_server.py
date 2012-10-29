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
    block in reactor.run() until you run 'stream_upload_test_client.py' which
    will write to its minimal example server.

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
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from txcloudfiles.cfobject import Object
from txcloudfiles import get_auth, UK_ENDPOINT, US_ENDPOINT

# make sure these are set in your shell
auth = get_auth(UK_ENDPOINT, os.environ.get('TXCFUSR', ''), os.environ.get('TXCFAPI', ''))

'''
    A simple socket protocol that starts up listening on 127.0.0.1:12345 and
    relays data as it's recieved.
'''

def unpack_header(header):
    # counterpart to pack_header in 'stream_upload_client.py'
    part_len = 32
    length, name, container, mimetype, md5hash = 0, '', '', '', ''
    try:
        length = int(header[0:part_len].strip())
    except ValueError:
        length = 0
    name = header[part_len:part_len*2].strip()
    container = header[part_len*2:part_len*3].strip()
    mimetype = header[part_len*3:part_len*4].strip()
    md5hash = header[part_len*4:part_len*5].strip()
    return length, name, container, mimetype, md5hash

class StreamingServerProtocol(Protocol):
    '''
        Relay data to a Cloud Files object.
    '''
    
    def __init__(self):
        # the raw header bytes
        self._raw_header = ''
        # set True when the header is recieved and unpacked
        self._got_header = False
        # header values (stream length, mime type, object name, container name and md5 hash)
        self._header = {'length': 0, 'type': '', 'name': '', 'container': '', 'hash': ''}
        # total length of expected header
        self._raw_header_len = len(self._header) * 32
        # buffer to store data in incase data is received but the upstream isn't quite ready
        self._buffer = []
        # the upstream transport
        self._upstream = None
        # deferred fired when we get a cloud files session
        self._s_ready = Deferred()
        # deferred fired when we have received and processed the incoming header
        self._d_ready = Deferred()
        # a list of deferreds, upload can only start once the header has been
        # received/processed and the connection upstream is open
        self._ready = DeferredList([self._s_ready, self._d_ready], consumeErrors=True)
        self._ready.addCallback(self._do_upload).addErrback(self._got_error)
    
    def connectionMade(self):
        # when we get an incoming connection start the handshake upstream to the
        # cloud files server
        auth.get_session().addCallback(self._got_session).addErrback(self._got_error)
    
    def _got_error(self, e):
        # there was an error creating the session or starting the object upload,
        # drop our client if present and stop the reactor if running
        print 'got error!'
        print
        print e
        print
        if self.connected:
            self.transport.loseConnection()
        if reactor.running:
            reactor.stop()
    
    def _got_session(self, session):
        # we created an upstream rackspace cloud files session, don't bother to
        # store this as a class attribute as you wantself._do_upload to request a new session
        # each time you need to use it incase the session expires in long running
        # processes
        print 'got session:', session
        self._s_ready.callback(('session', session))
    
    def dataReceived(self, data):
        print 'got:', len(data)
        # we know that there's a 160 byte header (5 * 32 bytes), see
        # 'stream_upload_test_client.py' for details on header
        if len(self._raw_header) < self._raw_header_len:
            # stuff on no more than 160 bytes
            self._raw_header += data[:self._raw_header_len]
            # save any left over
            data = data[self._raw_header_len:]
        # check to see if we've unpacked our simplistic header
        if len(self._raw_header) == self._raw_header_len and not self._got_header:
            # unpack the header
            length, name, container, mimetype, md5hash = unpack_header(self._raw_header)
            self._header = {'length': length, 'type': mimetype, 'name': name, 'container': container, 'hash': md5hash}
            self._got_header = True
            # we've unpacked the header OK, fire the deferred
            print 'got header:', self._header
            self._d_ready.callback(('header', self._header))
        # see if we have any data after checking for headers
        if data:
            # upstream transport is ready, write it directly
            if self._upstream:
                
                self._upstream.transport.write(data)
            # upstream isn't ready, store it in the buffer
            else:
                self._buffer.append(data)
    
    def _do_upload(self, r):
        # this is only called as the callback to the DeferredList, it fires when
        # we have a session and the header is unpacked - the buffer is likely
        # filling up at this point as well
        header = None
        session = None
        for (s, v) in r:
            what, value = v
            if what == 'header':
                header = value
            elif what == 'session':
                session = value
        # now we have the stream header and a session we can start the upload
        object_instance = Object(OBJECT_NAME)
        object_instance.set_content_type(self._type)
        object_instance.set_stream_len(self._expected_len)
        object_instance.set_stream(self.transport)
        session.stream_upload(CONTAINER_NAME, object_instance).addCallback(_ok).addErrback(_error)

server_factory = Factory()
server_factory.protocol = StreamingServerProtocol
server_endpoint = TCP4ServerEndpoint(reactor, 12345, interface='127.0.0.1')
server_endpoint.listen(server_factory)

reactor.run()

'''

    EOF

'''
