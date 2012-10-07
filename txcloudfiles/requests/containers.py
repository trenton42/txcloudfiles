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
from txcloudfiles.errors import NotAuthenticatedException, RequestException
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
    REQUIRED_HEADERS = ()
    REQUIRED_BODY = False
    EXPECTED_HEADERS = ()
    EXPECTED_BODY = Response.FORMAT_JSON
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response object wrappers '''

def list_containers(session):
    '''
        Returns a ContainerSet() object on success.
    '''
    d = Deferred()
    def _parse(r):
        if r.OK:
            containerset = ContainerSet()
            containerset.add_containers(r.json)
            d.callback(containerset)
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a list of containers, not authorised'))
        else:
            d.errback(RequestException('failed to get a list of containers'))
    request = ListContainersRequest(session)
    request.set_parser(_parse)
    request.run()
    return d

def list_all_containers(session, limit=10000):
    '''
        A slower and more elaborate version of list_containers. Performs
        sucessive recursive requests on accounts with large numbers of
        containers. Returns a single (and possibly very large)
        ContainerSet() object.
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
                d.callback(containerset)
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get a block of containers, not authorised'))
        else:
            d.errback(RequestException('failed to get a block of containers'))
    request = ListContainersRequest(session)
    request.set_parser(_parse)
    request.set_query_string(('limit', limit))
    request.run()
    return d

def create_container(session, name=''):
    '''
        Creates a container and returns boolean True on success.
    '''
    pass

def delete_container(session, container=None):
    '''
        Deletes a container and returns boolean True on success.
    '''

def _set_container_logging(session, container=None, enable=False):
    '''
        Enables or disables logging on a container.
    '''

def enable_logging(session, container=None):
    '''
        Wrapper for _set_container_logging to enable logging and returns
        boolean True on success.
    '''
    return _set_container_logging(container, True)

def disable_logging(session, container=None):
    '''
        Wrapper for _set_container_logging to disable logging.
    '''
    return _set_container_logging(container, False)

def get_container_metadata(session, container=None):
    '''
        Returns a Container object on success populated with metadata.
    '''

def set_container_metadata(session, container=None, metadata={}):
    '''
        Sets custom arbitrary metadata on a container and returns boolean
        True on success.
    '''
    pass

'''

    EOF

'''
