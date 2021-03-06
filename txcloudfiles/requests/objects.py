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

from time import mktime
from datetime import datetime
from twisted.internet.defer import Deferred
from txcloudfiles.transport import Request, Response
from txcloudfiles.errors import NotAuthenticatedException, ResponseException, CreateRequestException
from txcloudfiles.helpers import parse_int, parse_str, Metadata
from txcloudfiles.cfaccount import Account
from txcloudfiles.cfcontainer import Container, ContainerSet
from txcloudfiles.cfobject import Object

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

class RetrieveObjectRequest(Request):
    '''
        Get an object and all its data.
    '''
    METHOD = Request.GET
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL
    EXPECTED_BODY = Request.BINARY

class CreateObjectRequest(Request):
    '''
        Create an object.
    '''
    METHOD = Request.PUT
    REQUIRED_HEADERS = (
        'Content-Length',
    )
    REQUIRED_BODY = True
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class DeleteObjectRequest(Request):
    '''
        Delete an object.
    '''
    METHOD = Request.DELETE
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class ObjectMetadataRequest(Request):
    '''
        Get object metadata.
    '''
    METHOD = Request.HEAD
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class UpdateObjectMetadataRequest(Request):
    '''
        Update object metadata.
    '''
    METHOD = Request.POST
    REQUEST_TYPE = Request.REQUEST_STORAGE
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class CopyObjectRequest(Request):
    '''
        Copy an object to another container.
    '''
    METHOD = Request.COPY
    REQUEST_TYPE = Request.REQUEST_STORAGE
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
        sucessive recursive requests on accounts wiRetrieveObjectRequestth large numbers of 
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

def retrieve_object(session, container=None, obj=None):
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
        raise CreateRequestException('second argument must be an Object()  instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            object_name = r.request._object.get_name()
            obj = Object(name=object_name)
            obj.set_remote_hash(r.headers.get('ETag', ''))
            obj.set_content_type(r.headers.get('Content-Type', ''))
            obj.set_remote_lenth(r.headers.get('Content-Length', 0))
            obj.set_data(r.body)
            d.callback((r, obj))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to delete object, not authorised'))
        elif r.status_code == 404:
            d.errback(ResponseException('failed to delete object, object does not exist'))
        else:
            d.errback(ResponseException('failed to delete object'))
    request = RetrieveObjectRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_object(obj)
    request.run()
    return d

def create_object(session, container=None, obj=None, delete_at=None, metadata={}, cors={}):
    '''
        Create or replace an object into a container and returns a cfobject.Object()
        instance on success.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if not isinstance(obj, Object):
        raise CreateRequestException('second argument must be an Object()  instance or a string')
    _delete_at = 0
    if type(delete_at) == datetime and delete_at > datetime.now():
        _delete_at = mktime(delete_at.timetuple())
    d = Deferred()

    def _parse(r):
        if r.OK:
            if 'ETag' in r.headers and r.headers.get('ETag', '') != obj.get_hash():
                d.errback(ResponseException('failed to PUT data, upload hash mismatch (%s != %s)' % (r.headers.get('ETag', ''), obj.get_hash())))
            d.callback((r, obj))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to create object, not authorised'))
        elif r.status_code == 404:
            d.errback(ResponseException('failed to create object, container does not exist'))
        else:
            d.errback(ResponseException('failed to create object'))
    request = CreateObjectRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_object(obj)
    request.set_header(('Content-Length', obj.get_length()))
    request.set_header(('Etag', obj.get_hash()))
    if _delete_at > 0:
        request.set_header(('X-Delete-At', str(_delete_at)))
    for k, v in metadata.items():
        request.set_metadata((k, v), Metadata.OBJECT)
    if obj._content_type:
        request.set_header(('Content-Type', obj._content_type))
    if obj._compress:
        request.set_header(('Content-Encoding', 'gzip'))
    if obj._download_name:
        request.set_header(('Content-Disposition', 'attachment; %s' % obj._download_name))
    for k, v in cors.items():
        if k in Request.CORS_HEADERS:
            request.set_header((k, v))
    request.set_stream(obj.get_stream()) if obj.is_stream() else request.set_body(obj.get_data())
    request.run()
    return d

def delete_object(session, container=None, obj=None):
    '''
        Deletes an object and returns boolean True on success.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(obj, Object):
        raise CreateRequestException('second argument must be an Object()  instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to delete object, not authorised'))
        elif r.status_code == 404:
            d.errback(ResponseException('failed to delete object, object does not exist'))
        else:
            d.errback(ResponseException('failed to delete object'))
    request = DeleteObjectRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_object(obj)
    request.run()
    return d

def get_object_metadata(session, container=None, obj=None):
    '''
        Returns an Object object on success populated with metadata.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(obj, Object):
        raise CreateRequestException('second argument must be an Object()  instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            object_name = r.request._object.get_name()
            obj = Object(name=object_name)
            obj.set_metadata(r.metadata)
            d.callback((r, obj))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to set object metadata, not authorised'))
        elif r.status_code == 404:
            d.errback(NotAuthenticatedException('failed to set object metadata, object does not exist'))
        else:
            d.errback(ResponseException('failed to set object metadata'))
    request = ObjectMetadataRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_object(obj)
    request.run()
    return d

def set_object_metadata(session, container=None, obj=None, metadata={}):
    '''
        Sets custom arbitrary metadata on an object and returns boolean
        True on success.
    '''
    if type(obj) == str or type(obj) == unicode:
        obj = Object(name=obj)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(obj, Object):
        raise CreateRequestException('second argument must be an Object()  instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to set object metadata, not authorised'))
        elif r.status_code == 404:
            d.errback(ResponseException('failed to set object metadata, object does not exist'))
        else:
            d.errback(ResponseException('failed to set object metadata'))
    request = UpdateObjectMetadataRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_object(obj)
    for k,v in metadata.items():
        request.set_metadata((k, v), Metadata.OBJECT)
    request.run()
    return d

def copy_object(session, container_from, object_from, container_to, object_to):
    '''
        COPY's an Object() from one Container() to another, perserving metadata
        and optionally changing the Content-Type.
    '''
    if type(container_from) == str or type(container_from) == unicode:
        container_from = Container(container_from)
    if not isinstance(container_from, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    if type(object_from) == str or type(object_from) == unicode:
        object_from = Object(object_from)
    if not isinstance(object_from, Object):
        raise CreateRequestException('second argument must be an Object()  instance or a string')
    if type(container_to) == str or type(container_to) == unicode:
        container_to = Container(container_to)
    if not isinstance(container_to, Container):
        raise CreateRequestException('third argument must be a Container() instance or a string')
    if type(object_to) == str or type(object_to) == unicode:
        object_to = Object(object_to)
    if not isinstance(object_to, Object):
        raise CreateRequestException('fourth argument must be an Object()  instance or a string')
    d = Deferred()
    def _parse(r):
        if r.OK:
            d.callback((r, True))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to set object metadata, not authorised'))
        elif r.status_code == 404:
            d.errback(ResponseException('failed to set object metadata, object does not exist'))
        else:
            d.errback(ResponseException('failed to set object metadata'))
    request = CopyObjectRequest(session)
    request.set_parser(_parse)
    request.set_container(container_from)
    request.set_object(object_from)
    request.set_header(('Destination', '%s/%s' % (container_to.get_name(), object_to.get_name())))
    if object_from._content_type != object_to._content_type:
        request.set_header(('Content-Type', object_to._content_type))
    request.run()
    return d

def object_content_type(session, container, obj):
    '''
        Wrapper for copy_object which updates an objects Content-Type. First
        argument must be an Object() instance to have the _content_type property
        which is the only change.
    '''
    if not isinstance(obj, Object):
        raise CreateRequestException('second argument must be an Object()')
    return copy_object(session, container, obj.get_name(), container, obj)

'''
    EOF

'''
