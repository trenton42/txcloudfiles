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

    Provides request structure for CDN operations.

'''

from twisted.internet.defer import Deferred
from txcloudfiles.transport import Request, Response
from txcloudfiles.errors import NotAuthenticatedException, ResponseException
from txcloudfiles.helpers import parse_int, parse_str
from txcloudfiles.cfcontainer import Container, ContainerSet

''' requests '''

class ListCDNContainersRequest(Request):
    '''
        Get a list of containers.
    '''
    QUERY_STRING = {
        'format': 'json',
    }
    METHOD = Request.GET
    REQUEST_TYPE = Request.REQUEST_CDN
    EXPECTED_BODY = Response.FORMAT_JSON
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class EnableCDNContainerRequest(Request):
    '''
        CDN-enable an existing storage container.
    '''
    METHOD = Request.PUT
    REQUIRED_HEADERS = (
        'X-TTL',
        'X-Log-Retention',
    )
    REQUEST_TYPE = Request.REQUEST_CDN
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response object wrappers '''

def list_cdn_containers(session):
    '''
        Returns a ContainerSet() object populated with Containers() on success.
    '''
    d = Deferred()
    def _parse(r):
        if r.OK:
            containerset = ContainerSet()
            containerset.add_containers(r.json)
            d.callback((r, containerset))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a list of CDN containers, not authorised'))
        else:
            d.errback(ResponseException('failed to get a list of CDN containers'))
    request = ListCDNContainersRequest(session)
    request.set_parser(_parse)
    request.run()
    return d

def enable_cdn_container(session, container=None, ttl=0, logging=False):
    '''
        Enables public CDN access to a container and returns boolean a
        Container() object populated with some metadata on success.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    ttl = parse_int(ttl)
    ttl = session.CDN_TTL_MIN if ttl < session.CDN_TTL_MIN else ttl
    ttl = session.CDN_TTL_MAX if ttl > session.CDN_TTL_MAX else ttl
    logging = 'True' if logging else 'False'
    d = Deferred()
    def _parse(r):
        if r.OK:
            container = Container(
                name=r.request._container.get_name(),
                object_count=0,
                bytes=0,
                cdn=r.headers.get('X-Cdn-Enabled', False),
                logging=r.headers.get('X-Log-Retention', False),
                ttl=parse_int(r.headers.get('X-Ttl', 0)),
                cdn_uri=r.headers.get('X-Cdn-Uri', ''),
                ssl_uri=r.headers.get('X-Cdn-Ssl-Uri', ''),
                stream_uri=r.headers.get('X-Cdn-Streaming-Uri', '')
            )
            d.callback((r, container))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to CDN-enable container, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to CDN-enable container, container does not exist'))
        else:
            d.errback(ResponseException('failed to CDN-enable container'))
    request = EnableCDNContainerRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_header(('X-TTL', ttl))
    request.set_header(('X-Log-Retention', logging))
    request.run()
    return d

def disable_cdn_container(session, container=None):
    '''
        Disables public CDN access to a container and returns boolean True
        on success.
    '''
    pass

def get_cdn_container_metadata(session, container=None):
    '''
        Returns a Container object on success populated with metadata.
    '''
    pass

def set_cdn_container_metadata(session, container=None, metadata={}):
    '''
        Sets custom arbitrary metadata on a CDN enabled container and
        returns boolean True on success.
    '''
    pass

def purge_cdn_object(session, obj=None, container=None, email_addresses=()):
    '''
        Purges an object from a public CDN regardless of container TTL.
        Limited to 25 requests per day. Optional email addresses recieve a
        confirmation of the purge if set.
    '''
    pass

def set_cdn_container_index(session, container=None, index_file=''):
    '''
        Instructs Cloud Files to use the suppled file name as an index file
        for a CDN enabled container. Returns boolean True on success. 
    '''
    pass

def set_cdn_container_error(session, container=None, error_file=''):
    '''
        Instructs Cloud Files to use the suppled file name as an error file
        for a CDN enabled container for 401 and 404 errors. Returns boolean
        True on success. 
    '''
    pass

'''

    EOF

'''
