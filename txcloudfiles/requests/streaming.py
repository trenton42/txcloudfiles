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

    Provides request structure object streaming operations.

'''

from twisted.internet.defer import Deferred
from txcloudfiles.transport import Request, Response
from txcloudfiles.errors import NotAuthenticatedException, ResponseException, CreateRequestException
from txcloudfiles.helpers import parse_int, parse_str

''' requests '''

class StreamDownloadObjectRequest(Request):
    '''
        Get an object and all its data and return the data via a transport.
    '''
    METHOD = Request.GET
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class StreamUploadObjectRequest(Request):
    '''
        Create an object with streaming from a source transport.
    '''
    METHOD = Request.PUT
    REQUIRED_HEADERS = (
        'Content-Length',
    )
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response object wrappers '''

def stream_upload(session):
    '''
        Creates an object while streaming the body from a source twisted
        transport producer.
    '''
    pass

def stream_download(session):
    '''
        Retrieves an objects header then returns the body via a twisted
        transport producer.
    '''
    pass

'''

    EOF

'''
