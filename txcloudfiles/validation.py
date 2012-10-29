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

    Validation classes to provide relatively sane checking interfaces to
    Request() and Response() objects as well as some static constants.

'''

from urlparse import urlsplit, urlunsplit
from txcloudfiles.cfcontainer import Container
from txcloudfiles.helpers import parse_int, parse_str, Metadata
from txcloudfiles.cfobject import Object
from txcloudfiles.cfcontainer import Container
from txcloudfiles.errors import OperationConfigException, CreateRequestException

class DataFormatMixin(object):
    '''
        Validation mixin to provide the expected data type constants.
    '''
    
    FORMAT_BINARY = 'binary'
    FORMAT_JSON = 'json'
    FORMATS = (
        FORMAT_BINARY,
        FORMAT_JSON
    )
    BINARY = FORMAT_BINARY
    JSON = FORMAT_JSON
    REQUEST_AUTH = 0
    REQUEST_STORAGE = 1
    REQUEST_CDN = 2
    REQUEST_TYPES = (
        REQUEST_AUTH,
        REQUEST_STORAGE,
        REQUEST_CDN,
    )
    CORS_HEADERS = (
        'Access-Control-Allow-Credentials',
        'Access-Control-Allow-Methods',
        'Access-Control-Allow-Origin',
        'Access-Control-Expose-Headers',
        'Access-Control-Max-Age',
        'Access-Control-Request-Headers',
        'Access-Control-Request-Method',
        'Origin',
    )

class HTTPMethodMixin(object):
    '''
        Validation mixin to provide the expected HTTP request type constants.
    '''
    
    METHOD_GET = 'GET'
    METHOD_PUT = 'PUT'
    METHOD_POST = 'POST'
    METHOD_DELETE = 'DELETE'
    METHOD_HEAD = 'HEAD'
    METHOD_COPY = 'COPY'
    METHOD_OPTIONS = 'OPTIONS'
    METHODS = (
        METHOD_GET,
        METHOD_PUT,
        METHOD_POST,
        METHOD_DELETE,
        METHOD_HEAD,
        METHOD_COPY,
        METHOD_OPTIONS,
    )
    GET = METHOD_GET
    PUT = METHOD_PUT
    POST = METHOD_POST
    DELETE = METHOD_DELETE
    HEAD = METHOD_HEAD
    COPY = METHOD_COPY
    OPTIONS = METHOD_OPTIONS

class HTTPResponseMixin(object):
    '''
        Static list of all available HTTP response codes.
    '''
    
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

class GetValidationMixin(object):
    '''
        Validation mixin to provide sanity-checked interfaces to Request object
        static parameters.
    '''
    
    def _get_query_string(self):
        static_qs = getattr(self, 'QUERY_STRING', False)
        if static_qs:
            if type(static_qs) != dict:
                raise OperationConfigException('operation constant QUERY_STRING must be boolean False or a dictionary')
            static_qs_str = '&'.join(('%s=%s' % (k,v) for k,v in static_qs.items()))
        else:
            static_qs_str = ''
        qs = '&'.join(('%s=%s' % (k,v) for k,v in self._query_string.items())) + '&' + static_qs_str
        return '' if qs == '&' else qs
    
    def _get_request_method(self):
        method = getattr(self, 'METHOD', '')
        if method not in self.METHODS:
            raise OperationConfigException('operation constant METHOD must contain a valid METHOD')
        return method
    
    def _get_request_type(self):
        request_type = getattr(self, 'REQUEST_TYPE', '')
        if request_type not in self.REQUEST_TYPES:
            raise OperationConfigException('operation constant REQUEST_TYPE must contain a valid REQUEST_TYPE')
        return request_type
    
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
    
    def _get_required_body(self):
        return True if getattr(self, 'REQUIRED_BODY', False) else False
    
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
            if expected_response_code not in ResponseBase.HTTP_RESPONSE_CODES:
                raise OperationConfigException('operataion constant EXPECTED_RESPONSE_CODE must be a valid integer if set for a single response code')
            return expected_response_code
        elif type(expected_response_code) == tuple:
            if expected_response_code not in ResponseBase.HTTP_RESPONSE_CODE_GROUPS:
                raise OperationConfigException('operataion constant EXPECTED_RESPONSE_CODE must be a valid tuple of response code integers if set for a group of response codes')
            return expected_response_code
        raise OperationConfigException('operataion constant EXPECTED_RESPONSE_CODE valid integer or tuple of integers')
    
    def _get_request_headers(self):
        r = {}
        for k,v in self._request_headers.items():
            r[k] = [v]
        return r
    
    def _get_request_post(self):
        return self._request_post

class SetValidationMixin(object):
    '''
        Validation mixin to provide sanity-checked interfaces to Request object
        dynamic parameters.
    '''
    
    def set_header(self, header=()):
        if type(header) != tuple:
            raise OperationConfigException('set_header() must be called with a tuple as the only argument')
        if len(header) != 2:
            raise OperationConfigException('set_header() headers must be a tuple with exactly two values')
        self._request_headers[header[0]] = header[1]
    
    def set_metadata(self, metadata=(), prefix=None):
        if type(metadata) != tuple:
            raise OperationConfigException('set_metadata() must be called with a tuple as the only argument')
        if len(metadata) != 2:
            raise OperationConfigException('set_metadata() headers must be a tuple with exactly two values')
        self._request_headers[Metadata(prefix=prefix).prefix_header(metadata[0])] = metadata[1]
    
    def set_query_string(self, querystring=()):
        if type(querystring) != tuple:
            raise OperationConfigException('set_header() must be called with a tuple as the only argument')
        if len(querystring) != 2:
            raise OperationConfigException('set_header() headers must be a tuple with exactly two values')
        if querystring[1]:
            self._query_string[querystring[0]] = querystring[1]
    
    def set_body(self, body):
        if type(body) != str:
            raise OperationConfigException('set_body() must be called with a str as the only argument')
        self._body = body
    
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
    
    def set_stream(self, stream):
        self._stream = stream

class RequestValidationMixin(object):
    '''
        Validation mixin to assert Request() is properly constructed before
        sending it off.
    '''
    
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
        # check if a required body is set
        if self._get_required_body() and not self._body:
            raise CreateRequestException('required body is missing for request')

class RequestBase(GetValidationMixin, SetValidationMixin, RequestValidationMixin, DataFormatMixin, HTTPMethodMixin):
    '''
        Loads the above mixins as an extendable base.
    '''
    pass

class ResponseBase(HTTPResponseMixin, DataFormatMixin):
    '''
        Loads the above mixins as an extendable base.
    '''
    pass

class HTTPProtocol(HTTPMethodMixin, HTTPResponseMixin):
    '''
        Loads the above mixins as an extendable base.
    '''
    pass


'''

    EOF

'''
