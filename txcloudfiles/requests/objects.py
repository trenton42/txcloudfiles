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

def list_objects(session, container=None, prefix='', path='', delimiter=''):
    '''
        Returns a Container() populated with objects on success.
    '''
    if type(container) == str or type(container) == unicode:
        container = Container(name=container)
    if not isinstance(container, Container):
        raise CreateRequestException('first argument must be a Container() instance or a string')
    prefix = parse_str(prefix)
    path = parse_str(path)
    delimiter = parse_str(delimiter)[:1]
    d = Deferred()
    def _parse(r):
        if r.OK:
            container = Container()
            container.add_objects(r.json)
            d.callback((r, container))
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a list of objects, not authorised'))
        else:
            d.errback(ResponseException('failed to get a list of objects'))
    request = ListObjectsRequest(session)
    request.set_parser(_parse)
    request.set_container(container)
    request.set_query_string(('prefix', prefix))
    request.set_query_string(('path', path))
    request.set_query_string(('delimiter', delimiter))
    request.run()
    return d

def list_all_objects(session, container=None, limit=0, prefix='', path='', delimiter=''):
    '''
        A slower and more elaborate version of list_objects. Performs
        sucessive recursive requests on accounts with large numbers of 
        objects in a single container. Returns a single (and possibly very
        large) Container() object.
    '''
    pass

def get_object(session, obj=None):
    '''
        Retrieves the object, returns a blob of the object data on success.
    '''
    pass

def create_object(session, name='', container=None, delete_at=None, delete_after=None, metadata={}):
    '''
        Create or replace an object into a container and returns boolean
        True on success.
    '''
    pass

def delete_object(session, obj=None, container=None):
    '''
        Deletes an object and returns boolean True on success.
    '''
    pass

def get_object_metadata(session, obj=None, container=None):
    '''
        Returns a Container object on success populated with metadata.
    '''
    pass

def set_object_metadata(session, obj=None, container=None, metadata={}):
    '''
        Sets custom arbitrary metadata on a container and returns boolean
        True on success.
    '''
    pass

'''

    EOF

'''
