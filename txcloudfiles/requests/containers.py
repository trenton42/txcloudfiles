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

    Provides request structure for container operations.

'''

from twisted.internet.defer import Deferred
from txcloudfiles.transport import Request, Response
from txcloudfiles.errors import NotAuthenticatedException, ResponseException
from txcloudfiles.helpers import parse_int, parse_str
from txcloudfiles.cfcontainer import Container, ContainerSet

''' requests '''

class ListContainersRequest(Request):
    '''
        Get a list of containers.
    '''
    QUERY_STRING = {
        'format': 'json',
    }
    METHOD = Request.GET
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_BODY = Response.FORMAT_JSON
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class CreateContainerRequest(Request):
    '''
        Create a new container.
    '''
    METHOD = Request.PUT
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class DeleteContainerRequest(Request):
    '''
        Delete an existing empty container.
    '''
    METHOD = Request.DELETE
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class ContainerMetadataRequest(Request):
    '''
        Get container metadata.
    '''
    METHOD = Request.HEAD
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class UpdateContainerMetadataRequest(Request):
    '''
        Update container metadata.
    '''
    METHOD = Request.POST
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response object wrappers '''

def list_containers(session):
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
            d.errback(NotAuthenticatedException('failed to get a list of containers, not authorised'))
        else:
            d.errback(ResponseException('failed to get a list of containers'))
    request = ListContainersRequest(session)
    request.set_parser(_parse)
    request.run()
    return d

def list_all_containers(session, limit=10000):
    '''
        A slower and more elaborate version of list_containers. Performs
        sucessive recursive requests on accounts with large numbers of
        containers. Returns a single (and possibly very large) ContainerSet()
        populated with Containers() on success.
    '''
    limit = parse_int(limit)
    limit = session.CONTAINER_LIMIT if limit > session.CONTAINER_LIMIT else limit
    limit = session.CONTAINER_LIMIT if limit < 1 else limit
    d = Deferred()
    containerset = ContainerSet()
    def _parse(r):
        if r.OK:
            containerset.add_containers(r.json)
            if len(r.json) == limit:
                request = ListContainersRequest(session)
                request.set_parser(_parse)
                request.set_query_string(('limit', limit))
                request.set_query_string(('marker', containerset.get_last_container().get_name()))
                request.run()
            else:
                d.callback((r, containerset))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a block of containers, not authorised'))
        else:
            d.errback(ResponseException('failed to get a block of containers'))
    request = ListContainersRequest(session)
    request.set_parser(_parse)
    request.set_query_string(('limit', limit))
    request.run()
    return d

def create_container(session, name='', metadata={}):
    '''
        Creates a container and returns boolean True on success.
    '''
    name = parse_str(name)
    container = Container(name=name)
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to create container, not authorised'))
        else:
            d.errback(ResponseException('failed to create container'))
    request = CreateContainerRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    for k,v in metadata.items():
        request.set_metadata((k, v))
    request.run()
    return d

def delete_container(session, container=None):
    '''
        Deletes a container and returns boolean True on success.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to delete container, not authorised'))
        elif r.status_code == 404:
            d.errback(ResponseException('failed to delete container, container does not exist'))
        elif r.status_code == 409:
            d.errback(ResponseException('failed to delete container, container is not empty'))
        else:
            d.errback(ResponseException('failed to delete container'))
    request = DeleteContainerRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.run()
    return d

def get_container_metadata(session, container=None):
    '''
        Returns a Container object on success populated with metadata.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            container_name = r.request._container.get_name()
            container = Container(name=container_name, metadata=r.metadata)
            d.callback((r, container))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get container metadata, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to get container metadata, container does not exist'))
        else:
            d.errback(ResponseException('failed to get container metadata'))
    request = ContainerMetadataRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.run()
    return d

def set_container_metadata(session, container=None, metadata={}):
    '''
        Sets custom arbitrary metadata on a container and returns boolean
        True on success.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to set container metadata, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to set container metadata, container does not exist'))
        else:
            d.errback(ResponseException('failed to set container metadata'))
    request = UpdateContainerMetadataRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    for k,v in metadata.items():
        request.set_metadata((k, v))
    request.run()
    return d

def enable_container_logging(session, container=None):
    '''
        Wrapper for set_container_metadata to enable logging and returns
        boolean True on success.
    '''
    return set_container_metadata(session, container, {'X-Container-Meta-Access-Log-Delivery': True})

def disable_container_logging(session, container=None):
    '''
        Wrapper for set_container_metadata to disable logging and returns
        boolean True on success.
    '''
    return set_container_metadata(session, container, {'X-Container-Meta-Access-Log-Delivery': False})

def set_cdn_container_index(session, container=None, index_file=''):
    '''
        Instructs Cloud Files to use the suppled file name as an index file
        for a CDN enabled container, wrapper for set_container_metadata().
        Note this is actually a storage request and not a CDN request.
    '''
    return set_container_metadata(session, container, {'X-Container-Meta-Web-Index': index_file})

def set_cdn_container_error(session, container=None, error_file=''):
    '''
        Instructs Cloud Files to use the suppled file name as an error file
        for a CDN enabled container, wrapper for set_container_metadata().
        Note this is actually a storage request and not a CDN request.
    '''
    return set_container_metadata(session, container, {'X-Container-Meta-Web-Error': error_file})

'''

    EOF

'''
