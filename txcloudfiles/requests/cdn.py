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
from txcloudfiles.errors import NotAuthenticatedException, ResponseException, CreateRequestException
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

class CDNContainerMetadataRequest(Request):
    '''
        Get CDN-enabled container metadata request.
    '''
    METHOD = Request.HEAD
    REQUEST_TYPE = Request.REQUEST_CDN
    EXPECTED_HEADERS = (
        'X-Cdn-Uri',
        'X-Cdn-Ssl-Uri',
        'X-Cdn-Streaming-Uri',
    )
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class UpdateCDNContainerMetadataRequest(Request):
    '''
        Set CDN-enabled container metadata request.
    '''
    METHOD = Request.POST
    REQUEST_TYPE = Request.REQUEST_CDN
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class PurgeCDNObjectRequest(Request):
    '''
        Purge an live object from the CDN before the TTL expires. Limited to 25
        requests per account per day.
    '''
    METHOD = Request.DELETE
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

def set_cdn_container_metadata(session, container=None, metadata={}):
    '''
        Sets metadata on a CDN-enabled container and returns a Container()
        object on success populated with metadata.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    cdn = metadata.get('cdn', None)
    ttl = metadata.get('ttl', None)
    logging = metadata.get('logging', None)
    index_page = metadata.get('index_page', None)
    error_page = metadata.get('error_page', None)
    if cdn != None:
        cdn = True if cdn else False
    if ttl != None:
        ttl = parse_int(ttl)
        ttl = session.CDN_TTL_MIN if ttl < session.CDN_TTL_MIN else ttl
        ttl = session.CDN_TTL_MAX if ttl > session.CDN_TTL_MAX else ttl
    if logging != None:
        logging = True if logging else False
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
            d.errback(NotAuthenticatedException('failed to set CDN-enabled container metadata, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to set CDN-enabled container metadata, container does not exist'))
        else:
            d.errback(ResponseException('failed to set CDN-enabled container metadata'))
    request = UpdateCDNContainerMetadataRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    if cdn != None:
        request.set_header(('X-CDN-Enabled', cdn))
    if ttl != None:
        request.set_header(('X-TTL', ttl))
    if logging != None:
        request.set_header(('X-Log-Retention', logging))
    request.run()
    return d

def get_cdn_container_metadata(session, container=None):
    '''
        Returns a Container() object on success populated with metadata.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
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
            d.errback(NotAuthenticatedException('failed to get CDN container, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to get CDN container, container does not exist'))
        else:
            d.errback(ResponseException('failed to get CDN container'))
    request = CDNContainerMetadataRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.run()
    return d

def enable_cdn_container(session, container=None, ttl=None, logging=None):
    '''
        Enables public CDN access to a container, wrapper for
        set_cdn_container_metadata().
    '''
    metadata = {
        'cdn': True,
        'ttl': ttl,
        'logging': logging,
    }
    return set_cdn_container_metadata(session, container, metadata=metadata)


def disable_cdn_container(session, container=None):
    '''
        Disables public CDN access to a container, wrapper for
        set_cdn_container_metadata().
    '''
    metadata = {
        'cdn': False,
        'ttl': 0,
        'logging': None,
    }
    return set_cdn_container_metadata(session, container, metadata=metadata)

def purge_cdn_object(session, obj=None, container=None, email_addresses=()):
    '''
        Purges an object from a public CDN regardless of container TTL.
        Limited to 25 requests per day. Optional email addresses recieve a
        confirmation of the purge if set.
    '''
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to purge object from CDN, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to purge object from CDN, object or container does not exist'))
        else:
            d.errback(ResponseException('failed to purge object from CDN'))
    request = PurgeCDNObjectRequest(session)
    request.set_parser(_parse)
    if len(email_addresses) > 0:
        request.set_header(('X-Purge-Email', ', '.join(email_addresses)))
    request.run()
    return d

'''

    EOF

'''
