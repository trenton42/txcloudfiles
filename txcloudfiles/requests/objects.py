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

    Provides request structure for object operations.

'''

from twisted.internet.defer import Deferred
from txcloudfiles.transport import Request, Response
from txcloudfiles.errors import NotAuthenticatedException, ResponseException
from txcloudfiles.helpers import parse_int, parse_str
from txcloudfiles.cfaccount import Account
from txcloudfiles.cfcontainer import Container, ContainerSet

''' requests '''

class ListObjectsRequest(Request):
    '''
        Get a list of objects in a container.
    '''
    QUERY_STRING = {
        'format': 'json',
    }
    METHOD = Request.GET
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_BODY = Response.FORMAT_JSON
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response object wrappers '''

def list_objects(session, container=None, prefix=None, path=None, delimiter=None):
    '''
        Returns a Container() populated with objects on success.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            container = Container()
            container.add_objects(r.json)
            d.callback((r, container))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a list of objects, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to get a list of objects, container does not exist'))
        else:
            d.errback(ResponseException('failed to get a list of objects'))
    request = ListObjectsRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    if prefix != None:
        request.set_query_string(('prefix', parse_str(prefix)))
    if path != None:
        request.set_query_string(('path', parse_str(path)))
    if delimiter != None:
        request.set_query_string(('delimiter', parse_str(delimiter)[:1]))
    request.run()
    return d

def list_all_objects(session, container=None, limit=0, prefix=None, path=None, delimiter=None):
    '''
        A slower and more elaborate version of list_objects. Performs
        sucessive recursive requests on accounts with large numbers of 
        objects in a single container. Returns a single (and possibly very
        large) Container() object.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    limit = parse_int(limit)
    limit = session.CONTAINER_LIMIT if limit > session.CONTAINER_LIMIT else limit
    limit = session.CONTAINER_LIMIT if limit < 1 else limit
    d = Deferred()
    return_container = Container()
    def _parse(r):
        if r.OK:
            return_container.add_objects(r.json)
            if len(r.json) == limit:
                request = ListObjectsRequest(session)
                request.set_parser(_parse)
                request.set_container(container)
                request.set_query_string(('limit', limit))
                request.set_query_string(('marker', return_container.get_last_object().get_name()))
                if prefix != None:
                    request.set_query_string(('prefix', prefix))
                if path != None:
                    request.set_query_string(('path', path))
                if delimiter != None:
                    request.set_query_string(('delimiter', delimiter))
                request.run()
            d.callback((r, return_container))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a list of objects, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to get a list of objects, container does not exist'))
        else:
            d.errback(ResponseException('failed to get a list of objects'))
    request = ListObjectsRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_query_string(('limit', limit))
    if prefix != None:
        request.set_query_string(('prefix', parse_str(prefix)))
    if path != None:
        request.set_query_string(('path', parse_str(path)))
    if delimiter != None:
        request.set_query_string(('delimiter', parse_str(delimiter)[:1]))
    request.run()
    return d

def get_object(session, container=None, obj=None):
    '''
        Retrieves the object, returns a blob of the object data on success.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(obj, Object):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('second argument must be a Object() instance or a string')

def create_object(session, container=None, obj=None, delete_at=None, delete_after=None, metadata={}):
    '''
        Create or replace an object into a container and returns boolean
        True on success.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(obj, Object):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('second argument must be a Object() instance or a string')

def delete_object(session, container=None, obj=None):
    '''
        Deletes an object and returns boolean True on success.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(obj, Object):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('second argument must be a Object() instance or a string')

def get_object_metadata(session, container=None, obj=None):
    '''
        Returns a Container object on success populated with metadata.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(obj, Object):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('second argument must be a Object() instance or a string')

def set_object_metadata(sessio, container=None, obj=None, metadata={}):
    '''
        Sets custom arbitrary metadata on a container and returns boolean
        True on success.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(obj, Object):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('second argument must be a Object() instance or a string')

'''

    EOF

'''
