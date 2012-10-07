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
from txcloudfiles.errors import NotAuthenticatedException, RequestException
from txcloudfiles.helpers import parse_int, parse_str
from txcloudfiles.cfaccount import Account

''' requests '''

''' response object wrappers '''

def list_cdn_containers(session):
    '''
        Returns a ContainerSet() object on success.
    '''
    pass

def list_all_cdn_containers(session, limit=0):
    '''
        A slower and more elaborate version of list_cdn_containers. Performs
        sucessive recursive requests on accounts with large numbers of CDN
        enabled containers. Returns a single (and possibly very large)
        ContainerSet() object.
    '''
    pass

def enable_cdn_container(session, container=None, ttl=0):
    '''
        Enables public CDN access to a container and returns boolean a
        Container() object populated with some metadata on success.
    '''
    pass

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
