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

    Reverse proxy extension that can be used to build a high performance HTTP/S
    interface to Cloud Files.

'''

import urlparse
from urllib import quote as urlquote
from twisted.internet import reactor
from twisted.web.static import Data
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.proxy import ProxyClientFactory, ProxyClient
from twisted.web.resource import Resource
from twisted.internet.task import LoopingCall
from txcloudfiles.auth import Auth, Endpoint
from txcloudfiles.validation import HTTPProtocol
from txcloudfiles.helpers import Metadata

try:
    from txverifyssl.context import VerifyingSSLContext as SSLContextFactory
except ImportError:
    from twisted.internet.ssl import ClientContextFactory as SSLContextFactory

'''
    Returns a general error page with the correct HTTP status code.
'''
def render_error(request, code):
    html = '<html><body>'
    html += '<h1>%(code)s: %(title)s - %(error)s</h1>'
    html += '<p>%(desc)s</p>'
    html += '</body></html>'
    if code == HTTPProtocol.HTTP_BAD_GATEWAY:
        v = {
            'title': 'Bad Gateway',
            'error': 'Cloud Files session cannot be created',
            'desc': 'A Cloud Files session could not be created.'
        }
    elif code == HTTPProtocol.HTTP_SERVICE_UNAVAILABLE:
        v = {
            'title': 'Service Unavailable',
            'error': 'Cloud Files session not ready',
            'desc': 'A Cloud Files session does not currently exist, please try your request again.'
        }
    elif code == HTTPProtocol.HTTP_METHOD_NOT_ALLOWED:
        v = {
            'title': 'Method Not Allowed',
            'error': 'supplied method was not allowed',
            'desc': 'The method you used to access this resource was not allowed or was invalid.'
        }
    elif code == HTTPProtocol.HTTP_BAD_REQUEST:
        v = {
            'title': 'Bad Request',
            'error': 'supplied method was not allowed',
            'desc': 'The method you used to access this resource was not allowed or was invalid.'
        }
    elif code == HTTPProtocol.HTTP_UNAUTHORIZED:
        v = {
            'title': 'Unauthorized',
            'error': 'authorization failed',
            'desc': 'The method and request path combination you specified requires additional or valid authentication.'
        }
    else:
        code = HTTPProtocol.HTTP_INTERNAL_SERVER_ERROR
        v = {
            'title': 'Internal Server Error',
            'error': 'An error occured processing your request',
            'desc': 'There was an error processing your request, this is an issue with the server not your request.'
        }
    v['code'] = code
    request.responseHeaders.addRawHeader('Content-Type', 'text/html')
    request.setResponseCode(code, v['title'])
    return Data(html % v, 'text/html')

class ProxyRequestMap(object):
    '''
        Maps incoming requests to upstream CloudFiles requests.
    '''
    
    STATE_OK = 0
    STATE_ERROR_BAD_URI = 1
    STATE_ERROR_BAD_METHOD = 2
    
    def __init__(self, session):
        self.session = session
        # URI is /
        self.ROOT = {
            HTTPProtocol.GET: self.get_storage_location,
            HTTPProtocol.HEAD: self.get_storage_location,
        }
        # URI is /container
        self.CONTAINER = {
            HTTPProtocol.GET: self.get_storage_location,
            HTTPProtocol.PUT: self.get_storage_location,
            HTTPProtocol.DELETE: self.get_storage_location,
            HTTPProtocol.HEAD: self.get_storage_location,
            HTTPProtocol.POST: self.get_storage_location,
            HTTPProtocol.OPTIONS: self.get_cdn_location,
        }
        # URI is /container/object
        self.OBJECT = {
            HTTPProtocol.GET: self.get_storage_location,
            HTTPProtocol.PUT: self.get_storage_location,
            HTTPProtocol.DELETE: self.get_storage_location,
            HTTPProtocol.HEAD: self.get_storage_location,
            HTTPProtocol.POST: self.get_storage_location,
        }
    
    def handle(self, request):
        path = [p for p in urlquote(request.path, safe='').split('/') if p]
        func = False
        meta = None
        if len(path) == 0:
            # URI is /
            func = self.ROOT.get(request.method, False)
            meta = Metadata.ACCOUNT
        elif len(path) == 1:
            # URI is /container
            func = self.CONTAINER.get(request.method, False)
            meta = Metadata.CONTAINER
        elif len(path) == 2:
            # URI is /container/object
            func = self.OBJECT.get(request.method, False)
            meta = Metadata.OBJECT
        else:
            # invalid URI
            return (self.STATE_ERROR_BAD_URI, False, meta)
        if func:
            if func == self.get_cdn_location:
                meta = Metadata.CDN
            return (self.STATE_OK, func(path, request), meta)
        return (self.STATE_ERROR_BAD_METHOD, False, meta)
    
    def get_storage_location(self, path, request):
        parts = self.session.get_storage_url_parts()
        port = 443 if parts.scheme == 'https' else 80
        return parts.netloc, port, parts.path + request.path
    
    def get_cdn_location(self, path, request):
        parts = self.session.get_cdn_url_parts()
        port = 443 if parts.scheme == 'https' else 80
        return parts.netloc, port, parts.path + request.path

class CFProxyClient(ProxyClient):
    '''
        Intercepts all requests to map them to the expected CloudFiles API
        REST interface.
    '''

class CFProxyClientFactory(ProxyClientFactory):
    '''
        A client factory that just loads our custom ProxyClient.
    '''
    protocol = CFProxyClient
    
    def __init__(self, session, command, rest, version, headers, data, father):
        self.session = session
        self.father = father
        self.command = command
        self.rest = rest
        self.headers = headers
        self.data = data
        self.version = version

class CFProxyResource(Resource):
    '''
        Perform an upstream reqyest to the CloudFiles server.
    '''
    
    proxyClientFactoryClass = CFProxyClientFactory
    SESSION_TIMEOUT = 60*60*12
    
    def __init__(self, session, host='', port=0, path='', reactor=reactor):
        Resource.__init__(self)
        self.session = session
        self.host = host
        self.port = port
        self.path = path
        self.reactor = reactor
    
    def getChild(self, path, request):
        return CFProxyResource(
            self.session,
            self.host,
            self.port,
            self.path + '/' + urlquote(path, safe='')
        )
    
    def render(self, request):
        if self.port == 80:
            host = self.host
        else:
            host = "%s:%d" % (self.host, self.port)
        request.received_headers['host'] = host
        request.content.seek(0, 0)
        qs = urlparse.urlparse(request.uri)[4]
        if qs:
            rest = self.path + '?' + qs + '&format=json'
        else:
            rest = self.path + '?format=json'
        request_headers = request.getAllHeaders()
        request_headers['X-Auth-Token'] = self.session.get_key()
        clientFactory = self.proxyClientFactoryClass(
            self.session,
            request.method,
            rest,
            request.clientproto,
            request_headers,
            request.content.read(),
            request
        )
        if self.port == 443:
            context = SSLContextFactory()
            if hasattr(context, 'set_expected_host'):
                context.set_expected_host(self.host)
                context.raise_exception()
            self.reactor.connectSSL(self.host, self.port, clientFactory, context)
        else:
            self.reactor.connectTCP(self.host, self.port, clientFactory)
        return NOT_DONE_YET

class CFProxy(Resource):
    '''
        A reverse proxy resource that sits infront of a Cloud Files server and
        maps requests to an internal table before passing them on as a
        CFProxyResource request.
    '''
    
    proxyClientFactoryClass = CFProxyClientFactory
    SESSION_TIMEOUT = 60*60*12
    
    def __init__(self, auth, authenticator=None):
        Resource.__init__(self)
        self.auth = auth
        self.authenticator = authenticator
        self.session = None
        self.path = '/'
        self._refresh_session = LoopingCall(self._get_session)
        self._refresh_session.start(self.SESSION_TIMEOUT)
    
    def _get_session(self):
        def _got_session(session):
            self.session = session
        def _got_error(e):
            self.session = -1
        self.auth.get_session().addCallback(_got_session).addErrback(_got_error)
    
    def getChild(self, path, request):
        self.path = path
        return self.render(request)
    
    def render(self, request):
        if hasattr(self.authenticator, '__call__'):
            if not self.authenticator(str(request.method).upper(), request.getAllHeaders(), str(request.path)):
                return render_error(request, HTTPProtocol.HTTP_UNAUTHORIZED)
        if request.method not in HTTPProtocol.METHODS:
            return render_error(request, HTTPProtocol.HTTP_METHOD_NOT_ALLOWED)
        elif self.session == -1:
            return render_error(request, HTTPProtocol.HTTP_BAD_GATEWAY)
        elif not self.session:
            return render_error(request, HTTPProtocol.HTTP_SERVICE_UNAVAILABLE)
        state, meta, host, port, path = self._get_url(request)
        if state == ProxyRequestMap.STATE_ERROR_BAD_URI:
            return render_error(request, HTTPProtocol.HTTP_BAD_REQUEST)
        elif state == ProxyRequestMap.STATE_ERROR_BAD_METHOD:
            return render_error(request, HTTPProtocol.HTTP_METHOD_NOT_ALLOWED)
        return CFProxyResource(self.session, host, port, path)
    
    def _get_url(self, request):
        url_mapper = ProxyRequestMap(self.session)
        state, result, meta = url_mapper.handle(request)
        if state == ProxyRequestMap.STATE_OK:
            host, port, path = result
        else:
            host, port, path = '', 0, ''
        return state, meta, host, port, path

def get_proxy(endpoint, username, apikey, servicenet=False, authenticator=None):
    '''
        Wrapper to generate and return a populated CFProxy instance.
    '''
    auth = Auth(Endpoint(endpoint, servicenet), username, apikey)
    return Site(CFProxy(auth, authenticator=authenticator))

'''

    EOF

'''
