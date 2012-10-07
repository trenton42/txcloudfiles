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
from txcloudfiles.helpers import parse_int, parse_str
from txcloudfiles.cfcontainer import Container
from txcloudfiles.cfobject import Object
from txcloudfiles.errors import OperationConfigException, CreateRequestException

# try and import the verifying SSL context from txverifyssl
try:
    from txverifyssl.context import VerifyingSSLContext as SSLContextFactory
except ImportError:
    from twisted.internet.ssl import ClientContextFactory as SSLContextFactory

USER_AGENT = 'txcloudfiles v%s' % __version__

class Request(object):
    '''
        Transport layer which operations can use to make requests to the Cloud
        Files API. Translates responses into Response() or ResponseError()
        objects.
    '''
    
    METHOD_GET = 'GET'
    METHOD_PUT = 'PUT'
    METHOD_POST = 'POST'
    METHOD_DELETE = 'DELETE'
    METHOD_HEAD = 'HEAD'
    METHODS = (
        METHOD_GET,
        METHOD_PUT,
        METHOD_POST,
        METHOD_DELETE,
        METHOD_HEAD,
    )
    
    FORMAT_BINARY = 'binary'
    FORMAT_JSON = 'json'
    FORMATS = (
        FORMAT_BINARY,
        FORMAT_JSON
    )
    
    # aliases
    GET = METHOD_GET
    PUT = METHOD_PUT
    POST = METHOD_POST
    DELETE = METHOD_DELETE
    HEAD = METHOD_HEAD
    BINARY = FORMAT_BINARY
    JSON = FORMAT_JSON
    
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
    
    def _get_query_string(self):
        static_qs = getattr(self, 'QUERY_STRING', False)
        if static_qs:
            if type(static_qs) != dict:
                raise OperationConfigException('operation constant QUERY_STRING must be boolean False or a dictionary')
            static_qs_str = '&'.join(('%s=%s' % (k,v) for k,v in static_qs.items()))
        else:
            static_qs_str = ''
        return '&'.join(('%s=%s' % (k,v) for k,v in self._query_string.items())) + '&' + static_qs_str
    
    def _get_request_method(self):
        method = getattr(self, 'METHOD', '')
        if method not in self.METHODS:
            raise OperationConfigException('operation constant METHOD must contain a valid METHOD')
        return method
    
    def _get_request_auth(self):
        return True if getattr(self, 'AUTH_REQUEST', False) else False
    
    def _get_request_management(self):
        return True if getattr(self, 'MANAGEMENT_REQUEST', False) else False
    
    def _get_required_headers(self):
        required_headers = getattr(self, 'REQUIRED_HEADERS', '')
        if type(required_headers) != tuple:
            raise OperationConfigException('operataion constant REQUIRED_HEADERS must be a tuple')
        return required_headers
    
    def _get_required_post(self):
        required_post = getattr(self, 'REQUIRED_POST', '')
        if type(required_post) != bool:
            raise OperationConfigException('operataion constant REQUIRED_POST must be a boolean')
        return required_post
    
    def _get_expected_headers(self):
        expected_headers = getattr(self, 'EXPECTED_HEADERS', '')
        if type(expected_headers) != tuple:
            raise OperationConfigException('operataion constant EXPECTED_HEADERS must be a tuple')
        return expected_headers
    
    def _get_expected_body(self):
        expected_body = getattr(self, 'EXPECTED_BODY', '')
        if type(expected_body) != bool and expected_body not in self.FORMATS:
            raise OperationConfigException('operataion constant EXPECTED_BODY must be a valid FORMAT or boolean')
        return expected_body
    
    def _get_expected_response_code(self):
        expected_response_code = getattr(self, 'EXPECTED_RESPONSE_CODE', '')
        if type(expected_response_code) == int:
            if expected_response_code not in Response.HTTP_RESPONSE_CODES:
                raise OperationConfigException('operataion constant EXPECTED_RESPONSE_CODE must be a valid integer if set for a single response code')
            return expected_response_code
        elif type(expected_response_code) == tuple:
            if expected_response_code not in Response.HTTP_RESPONSE_CODE_GROUPS:
                raise OperationConfigException('operataion constant EXPECTED_RESPONSE_CODE must be a valid tuple of response code integers if set for a group of response codes')
            return expected_response_code
        raise OperationConfigException('operataion constant EXPECTED_RESPONSE_CODE valid integer or tuple of integers')
    
    def _get_request_url(self):
        if self._get_request_auth():
            endpoint = self._session.get_endpoint()
            return endpoint.get_auth_url()
        if self._get_request_management():
            parts = self._session.get_storage_url_parts()
        else:
            parts = self._session.get_storage_url_parts()
        path = parts.path
        if isinstance(self._container, Container):
            path += '/' + self._container.get_name()
            if isinstance(self._object, Object):
                path += '/' + self._object.get_name()
        qs = parts.query + self._get_query_string()
        request_url = urlunsplit((parts.scheme, parts.netloc, path, qs, parts.fragment))
        #print '-'*80
        #print request_url
        #print '-'*80
        return parse_str(request_url)
    
    def _get_request_headers(self):
        return self._request_headers
    
    def _get_request_post(self):
        return self._request_post
    
    def set_header(self, header=()):
        if type(header) != tuple:
            raise OperationConfigException('set_header() must be called with a tuple as the only argument')
        if len(header) != 2:
            raise OperationConfigException('set_header() headers must be a tuple with exactly two values')
        self._request_headers[header[0]] = header[1]
    
    def set_query_string(self, querystring=()):
        if type(querystring) != tuple:
            raise OperationConfigException('set_header() must be called with a tuple as the only argument')
        if len(querystring) != 2:
            raise OperationConfigException('set_header() headers must be a tuple with exactly two values')
        if querystring[1]:
            self._query_string[querystring[0]] = querystring[1]
    
    def set_container(self, container):
        if not isinstance(container, Container):
            raise OperationConfigException('set_container() must be called with a Container() instance as the only argument')
        self._container = container
    
    def set_object(self, obj):
        if not isinstance(obj, Object):
            raise OperationConfigException('set_object() must be called with a Object() instance as the only argument')
        self._object = obj
    
    def set_post(self, post={}):
        if type(post) != dict:
            raise OperationConfigException('set_post() must be called with a dictionary as the only argument')
        self._request_post = post
    
    def set_parser(self, callback):
        if not hasattr(callback, '__call__'):
            raise OperationConfigException('set_parser() must be called with a callback function as the only argument')
        self._request_parser = callback
    
    def _validate_request(self):
        '''
            Checks the combination of request information is valid.
        '''
        # check we have a response parser
        if not self._request_parser:
            raise OperationConfigException('required parser missing for request')
        # check required request headers are set
        for header in self._get_required_headers():
            if header not in self._request_headers:
                raise CreateRequestException('required header missing for request: %s' % header)
        # check post data is set for POST requests
        if self._get_required_post() and len(self._request_post) == 0:
            raise CreateRequestException('required post data is missing for request')
    
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
        return headers
    
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
            headers = self._parse_headers(factory.response_headers)
            actual_code, status_code = self._verify_response(factory.status, headers, binary_data, json_data)
            response_class = Response if status_code > 0 else ResponseError
            self._request_parser(response_class(
                request=self,
                status_code=actual_code,
                headers=factory.response_headers,
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

class Response(object):
    '''
    
        The response object populated with data from a request.
    
    '''
    
    OK = True
    
    # response codes and response code groups
    HTTP_CONTINUE = 100
    HTTP_SWITCHING_PROTOCOLS = 101
    HTTP_SUCCESSFUL = 102
    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_ACCEPTED = 202
    HTTP_NOT_AUTHORITATIVE = 203
    HTTP_NO_CONTENT = 204
    HTTP_RESET_CONTENT = 205
    HTTP_PARTIAL_CONTENT = 206
    HTTP_MULTIPLE_CHOICES = 300
    HTTP_MOVED_PERMANENTLY = 301
    HTTP_FOUND = 302
    HTTP_SEE_OTHER = 303
    HTTP_NOT_MODIFIED = 304
    HTTP_USE_PROXY = 305
    HTTP_TEMPORARY_REDIRECT = 307
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_PAYMENT_REQUIRED = 402
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_METHOD_NOT_ALLOWED = 405
    HTTP_NOT_ACCEPTABLE = 406
    HTTP_PROXY_AUTHENTICATION_REQUIRED = 407
    HTTP_REQUEST_TIMEOUT = 408
    HTTP_CONFLICT = 409
    HTTP_GONE = 410
    HTTP_LENGTH_REQUIRED = 411
    HTTP_PRECONDITION_FAILED = 412
    HTTP_REQUEST_ENTITY_TOO_LARGE = 413
    HTTP_REQUEST_URI_TOO_LONG = 414
    HTTP_UNSUPPORTED_MEDA_TYPE = 415
    HTTP_REQUEST_RANGE_NOT_SATISFIABLE = 416
    HTTP_EXPECTATION_FAILED = 417
    HTTP_RATE_LIMITED = 498
    HTTP_INTERNAL_SERVER_ERROR = 500
    HTTP_NOT_IMPLEMENTED = 501
    HTTP_BAD_GATEWAY = 502
    HTTP_SERVICE_UNAVAILABLE = 503
    HTTP_GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    HTTP_INFORMATIONAL = (
        HTTP_CONTINUE,
        HTTP_SWITCHING_PROTOCOLS,
        HTTP_SUCCESSFUL,
    )
    HTTP_SUCCESSFUL = (
        HTTP_OK,
        HTTP_CREATED,
        HTTP_ACCEPTED,
        HTTP_NOT_AUTHORITATIVE,
        HTTP_NO_CONTENT,
        HTTP_RESET_CONTENT,
        HTTP_PARTIAL_CONTENT,
    )
    HTTP_REDIRECTION = (
        HTTP_MULTIPLE_CHOICES,
        HTTP_MOVED_PERMANENTLY,
        HTTP_FOUND,
        HTTP_SEE_OTHER,
        HTTP_NOT_MODIFIED,
        HTTP_USE_PROXY,
        HTTP_TEMPORARY_REDIRECT,
    )
    HTTP_CLIENT_ERROR = (
        HTTP_BAD_REQUEST,
        HTTP_UNAUTHORIZED,
        HTTP_PAYMENT_REQUIRED,
        HTTP_FORBIDDEN,
        HTTP_NOT_FOUND,
        HTTP_METHOD_NOT_ALLOWED,
        HTTP_NOT_ACCEPTABLE,
        HTTP_PROXY_AUTHENTICATION_REQUIRED,
        HTTP_REQUEST_TIMEOUT,
        HTTP_CONFLICT,
        HTTP_GONE,
        HTTP_LENGTH_REQUIRED,
        HTTP_PRECONDITION_FAILED,
        HTTP_REQUEST_ENTITY_TOO_LARGE,
        HTTP_REQUEST_URI_TOO_LONG,
        HTTP_UNSUPPORTED_MEDA_TYPE,
        HTTP_REQUEST_RANGE_NOT_SATISFIABLE,
        HTTP_EXPECTATION_FAILED,
        HTTP_RATE_LIMITED,
    )
    HTTP_SERVER_ERROR = (
        HTTP_INTERNAL_SERVER_ERROR,
        HTTP_NOT_IMPLEMENTED,
        HTTP_BAD_GATEWAY,
        HTTP_SERVICE_UNAVAILABLE,
        HTTP_GATEWAY_TIMEOUT,
        HTTP_VERSION_NOT_SUPPORTED,
    )
    HTTP_RESPONSE_CODES = HTTP_INFORMATIONAL + HTTP_SUCCESSFUL + HTTP_REDIRECTION + HTTP_CLIENT_ERROR + HTTP_SERVER_ERROR
    HTTP_RESPONSE_CODE_GROUPS = (
        HTTP_INFORMATIONAL,
        HTTP_SUCCESSFUL,
        HTTP_REDIRECTION,
        HTTP_CLIENT_ERROR,
        HTTP_SERVER_ERROR,
    )
    
    FORMAT_BINARY = 'binary'
    FORMAT_JSON = 'json'
    FORMATS = (
        FORMAT_BINARY,
        FORMAT_JSON
    )
    
    def __init__(self, request=None, status_code=0, headers={}, binary_body='', json_body={}, body_type=Request.FORMAT_JSON):
        self.request = request
        if status_code in self.HTTP_RESPONSE_CODES:
            self.status_code = status_code
        else:
            self.status_code = 0
        self.headers = headers
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
