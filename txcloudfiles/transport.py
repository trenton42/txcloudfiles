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

    Transport provides the generic wrapper interface to the Cloud Files API
    endpoint allowing the commands to ignore the authentication details.

'''

import json
from urllib import urlencode
from urlparse import urlsplit, urlunsplit
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.web.client import HTTPClientFactory
from twisted.python.failure import Failure
from txcloudfiles import __version__
from txcloudfiles.validation import RequestBase, ResponseBase
from txcloudfiles.helpers import parse_int, Metadata

# try and import the verifying SSL context from txverifyssl
try:
    from txverifyssl.context import VerifyingSSLContext as SSLContextFactory
except ImportError:
    from twisted.internet.ssl import ClientContextFactory as SSLContextFactory

USER_AGENT = 'txcloudfiles v%s' % __version__

class Request(RequestBase):
    '''
        Transport layer which operations can use to make requests to the Cloud
        Files API. Translates responses into Response() or ResponseError()
        objects.
    '''
    
    # overridden by operations
    QUERY_STRING = False
    METHOD = False
    AUTH_REQUEST = False
    MANAGEMENT_REQUEST = False
    REQUIRED_HEADERS = ()
    REQUIRED_POST = False
    EXPECTED_HEADERS = ()
    EXPECTED_BODY = False
    EXPECTED_RESPONSE_CODE = False
    
    # optionally overridden
    TIMEOUT = 15
    REDIRECT_LIMIT = 0
    
    def __init__(self, session):
        self._session = session
        self._request_headers = {}
        self._request_post = {}
        self._request_parser = None
        self._waiting = False
        self._query_string = {}
        self._container = None
        self._object = None
    
    def _construct_post_data(self):
        data = self._get_request_post()
        if type(data) == dict:
            return urlencode(data)
        return ''
    
    def _parse_response_data(self, data):
        if isinstance(data, Failure):
            binary_data, json_data = '', {}
        #print '-'*80
        #print data
        #print '-'*80
        expected_body = self._get_expected_body()
        if expected_body == self.FORMAT_BINARY:
            binary_data, json_data = data, {}
        elif expected_body == self.FORMAT_JSON:
            try:
                binary_data, json_data = '', json.loads(data)
            except ValueError:
                binary_data, json_data = '', {}
        return binary_data, json_data
    
    def _parse_headers(self, headers):
        if type(headers) != dict:
            return {}
        for k,v in headers.items():
            headers[k.title()] = v if type(v) != list else v[0]
        return headers, Metadata().loads(headers)
    
    def _verify_response(self, status_code, headers, binary_data, json_data):
        status_code = parse_int(status_code)
        expected_status_code = self._get_expected_response_code()
        if type(expected_status_code) == int and status_code != expected_status_code:
            return status_code, 0
        elif type(expected_status_code) == tuple and status_code not in expected_status_code:
            return status_code, 0
        for header in self._get_expected_headers():
            if header not in headers:
                return status_code, 0
        if self._get_expected_body() == self.FORMAT_BINARY and not binary_data and status_code != 204:
            return status_code, 0
        if self._get_expected_body() == self.FORMAT_JSON and type(json_data) != list and type(json_data) != dict and status_code != 204:
            return status_code, 0
        return status_code, status_code
    
    def _do_request(self):
        '''
            Constructs a request using the child operation parameters and
            returns an HTTPClientFactory instance.
        '''
        
        def _got_data(data, factory):
            '''
                Check the response for failure. Note twisted raises a 'Failure'
                for things like HTTP 204's with no content, despite this being
                normal behaviour for the API.
            '''
            binary_data, json_data = self._parse_response_data(data)
            headers, metadata = self._parse_headers(factory.response_headers)
            actual_code, status_code = self._verify_response(factory.status, headers, binary_data, json_data)
            response_class = Response if status_code > 0 else ResponseError
            self._request_parser(response_class(
                request=self,
                status_code=actual_code,
                headers=factory.response_headers,
                metadata=metadata,
                binary_body=binary_data,
                json_body=json_data,
                body_type=self._get_expected_body()
            ))
        
        if not self._get_request_auth():
            self.set_header(('X-Auth-Token', self._session.get_key()))
        url = self._get_request_url()
        factory = HTTPClientFactory(
            url,
            method=self._get_request_method(),
            postdata=self._construct_post_data(),
            headers=self._get_request_headers(),
            agent=USER_AGENT,
            timeout=self.TIMEOUT,
            cookies=None,
            followRedirect=(1 if self.REDIRECT_LIMIT > 0 else 0),
            redirectLimit=self.REDIRECT_LIMIT
        )
        parts = urlsplit(url)
        custom_port = parts.netloc.find(':')
        port = 0
        if custom_port > 0:
            port = parts.netloc[custom_port+1:]
            port = parse_int(port)
        if port == 0:
            port = 443 if parts.scheme == 'https' else 80
        if parts.scheme == 'https':
            reactor.connectSSL(parts.netloc, port, factory, SSLContextFactory(url))
        else:
            reactor.connectTCP(parts.netloc, port, factory)
        factory.deferred.addCallback(_got_data, factory)
        factory.deferred.addErrback(_got_data, factory)
    
    def run(self):
        '''
            Perform a request.
        '''
        self._validate_request()
        self._do_request()
        return True

class Response(ResponseBase):
    '''
    
        The response object populated with data from a request.
    
    '''
    
    OK = True
    
    def __init__(self, request=None, status_code=0, headers={}, metadata={}, binary_body='', json_body={}, body_type=Request.FORMAT_JSON):
        self.request = request
        if status_code in self.HTTP_RESPONSE_CODES:
            self.status_code = status_code
        else:
            self.status_code = 0
        self.headers = headers
        self.metadata = metadata
        self.body = binary_body
        self.json = json_body
        self.body_type = body_type

class ResponseError(Response):
    '''
        A Respone() which generated a serious (non-HTTP, such as a socket issue)
        error.
    '''
    
    OK = False

'''

    EOF

'''
