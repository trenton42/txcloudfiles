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

    A session is a self-verifying authentication storage object as well as
    containing top level request wrappers to construct Account() and Container()
    objects.

'''

from time import time
from urlparse import urlsplit
from twisted.internet.defer import Deferred
from helpers import parse_int, parse_str
from errors import NotAuthenticatedException, RequestException, CreateRequestException
from requests import account, containers, objects
from cfaccount import Account
from cfcontainer import ContainerSet, Container
from cfobject import Object

class Session(object):
    '''
        Holds a single authentication session and provides the main top level
        programming interface to the Cloud Files account to perform most
        operations on the account, containers and objects.
    '''
    
    # while the documentation says authtokens are valid for 24h set it to 12h
    # (in seconds) which means unless you're doing something really weird (such
    # as single session operations taking over 12 hours) it won't ever expire
    AUTH_TIMELIMIT = 43200
    # the maximum containers we can expect to ask for (from API docs)
    CONTAINER_LIMIT = 10000
    # the maximum objects we can expect to ask for (from API docs)
    OBJECT_LIMIT = 10000
    # minimum allowed TTL for CDN containers in seconds (from API docs)
    CDN_TTL_MIN = 900
    # maximum allowed TTL for CDN containers in seconds (from API docs)
    CDN_TTL_MAX = 1576800000
    
    def __init__(self, username='', key='', storage_url='', management_url='', servicenet=''):
        self._timer = time() if key else 0
        self._username = username if username else ''
        self._key = key if key else ''
        self._storage_url = storage_url
        self._management_url = management_url
        self._storage_url_parts = urlsplit(storage_url)
        self._management_url_parts = urlsplit(management_url)
        self._servicenet = ''
    
    def _is_valid(self):
        if self._timer == 0 or not self._key:
            raise NotAuthenticatedException('token not set')
        elif self._timer < time() - self.AUTH_TIMELIMIT:
            raise NotAuthenticatedException('token has expired')
        return True
        
    def is_valid(self):
        try:
            valid = self._is_valid()
        except NotAuthenticatedException:
            valid = False
        return valid
    
    def get_key(self):
        if self.is_valid():
            return self._key
        return ''
    
    def get_storage_url_parts(self):
        if self._servicenet:
            self._storage_url_parts.netloc = self._servicenet + self._storage_url_parts.netloc
        return self._storage_url_parts
    
    def get_management_url_parts(self):
        return self._management_url_parts
    
    ''' account request wrappers '''
    
    def get_account_metadata(self):
        '''
            Returns an Account object on success populated with metadata.
        '''
        d = Deferred()
        def _parse(r):
            if r.OK:
                a = Account(self._username)
                a.set_container_count(r.headers.get('X-Account-Container-Count', ''))
                a.set_bytes_used(r.headers.get('X-Account-Bytes-Used', ''))
                d.callback(a)
            elif r.status_code == 401:
                d.errback(NotAuthenticatedException('failed to get account information, not authorised'))
            else:
                d.errback(RequestException('failed to get account information'))
        request = account.AccountMetadataRequest(self)
        request.set_parser(_parse)
        request.run()
        return d
    
    def set_temp_url_key(self, key):
        '''
            Returns boolean True on success.
        '''
        key = parse_str(key)
        d = Deferred()
        def _parse(r):
            if r.OK:
                d.callback(True)
            elif r.status_code == 401:
                d.errback(NotAuthenticatedException('failed to set temp url key, not authorised'))
            else:
                d.errback(RequestException('failed to set the account key'))
        request = account.AccountSetTempURLKeyRequest(self)
        request.set_header(('X-Account-Meta-Temp-Url-Key', key))
        request.set_parser(_parse)
        request.run()
        return d
    
    ''' container request wrappers '''
    
    def list_containers(self):
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
        request = containers.ListContainersRequest(self)
        request.set_parser(_parse)
        request.run()
        return d
    
    def list_all_containers(self, limit=10000):
        '''
            A slower and more elaborate version of list_containers. Performs
            sucessive recursive requests on accounts with large numbers of
            containers. Returns a single (and possibly very large)
            ContainerSet() object.
        '''
        limit = parse_int(limit)
        limit = self.CONTAINER_LIMIT if limit > self.CONTAINER_LIMIT else limit
        limit = self.CONTAINER_LIMIT if limit < 1 else limit
        d = Deferred()
        containerset = ContainerSet()
        def _parse(r):
            if r.OK:
                containerset.add_containers(r.json)
                if len(r.json) == limit:
                    request = containers.ListContainersRequest(self)
                    request.set_parser(_parse)
                    request.set_query_string(('limit', limit))
                    request.set_query_string(('marker', containerset.get_last_container()))
                    request.run()
                else:
                    d.callback(containerset)
            elif r.status_code == 401:
                d.errback(NotAuthenticatedException('failed to get a block of containers, not authorised'))
            else:
                d.errback(RequestException('failed to get a block of containers'))
        request = containers.ListContainersRequest(self)
        request.set_parser(_parse)
        request.set_query_string(('limit', limit))
        request.run()
        return d
    
    def create_container(self, name=''):
        '''
            Creates a container and returns boolean True on success.
        '''
        pass
    
    def delete_container(self, container=None):
        '''
            Deletes a container and returns boolean True on success.
        '''
    
    def _set_container_logging(self, container=None, enable=False):
        '''
            Enables or disables logging on a container.
        '''
    
    def enable_logging(self, container=None):
        '''
            Wrapper for _set_container_logging to enable logging and returns
            boolean True on success.
        '''
        return self._set_container_logging(container, True)
    
    def disable_logging(self, container=None):
        '''
            Wrapper for _set_container_logging to disable logging.
        '''
        return self._set_container_logging(container, False)
    
    def get_container_metadata(self, container=None):
        '''
            Returns a Container object on success populated with metadata.
        '''
    
    def set_container_metadata(self, container=None, metadata={}):
        '''
            Sets custom arbitrary metadata on a container and returns boolean
            True on success.
        '''
        pass
    
    ''' object request wrappers '''
    
    def list_objects(self, container=None, prefix='', path='', delimiter=''):
        '''
            Returns an ObjectSet() object on success.
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
                d.callback(container)
            elif r.status_code == 401:
                d.errback(NotAuthenticatedException('failed to get a list of objects, not authorised'))
            else:
                d.errback(RequestException('failed to get a list of objects'))
        request = objects.ListObjectsRequest(self)
        request.set_parser(_parse)
        request.set_container(container)
        request.run()
        return d
    
    def list_all_objects(self, container=None, limit=0, prefix='', path='', delimiter=''):
        '''
            A slower and more elaborate version of list_objects. Performs
            sucessive recursive requests on accounts with large numbers of 
            objects in a single container. Returns a single (and possibly very
            large) Container() object.
        '''
        pass
    
    def get_object(self, obj=None):
        '''
            Retrieves the object, returns a blob of the object data on success.
        '''
        pass
    
    def create_object(self, name='', container=None, delete_at=None, delete_after=None, metadata={}):
        '''
            Create or replace an object into a container and returns boolean
            True on success.
        '''
        pass
    
    def delete_object(self, obj=None, container=None):
        '''
            Deletes an object and returns boolean True on success.
        '''
        pass

    def get_object_metadata(self, obj=None, container=None):
        '''
            Returns a Container object on success populated with metadata.
        '''
    
    def set_object_metadata(self, obj=None, container=None, metadata={}):
        '''
            Sets custom arbitrary metadata on a container and returns boolean
            True on success.
        '''
    
    ''' object request wrappers '''
    
    def list_cdn_containers(self):
        '''
            Returns a ContainerSet() object on success.
        '''
        pass
    
    def list_all_cdn_containers(self, limit=0):
        '''
            A slower and more elaborate version of list_cdn_containers. Performs
            sucessive recursive requests on accounts with large numbers of CDN
            enabled containers. Returns a single (and possibly very large)
            ContainerSet() object.
        '''
        pass
    
    def enable_cdn_container(self, container=None, ttl=0):
        '''
            Enables public CDN access to a container and returns boolean a
            Container() object populated with some metadata on success.
        '''
        pass
    
    def disable_cdn_container(self, container=None):
        '''
            Disables public CDN access to a container and returns boolean True
            on success.
        '''
        pass
    
    def get_cdn_container_metadata(self, container=None):
        '''
            Returns a Container object on success populated with metadata.
        '''
        pass
    
    def set_cdn_container_metadata(self, container=None, metadata={}):
        '''
            Sets custom arbitrary metadata on a CDN enabled container and
            returns boolean True on success.
        '''
        pass
    
    def purge_cdn_object(self, obj=None, container=None, email_addresses=()):
        '''
            Purges an object from a public CDN regardless of container TTL.
            Limited to 25 requests per day. Optional email addresses recieve a
            confirmation of the purge if set.
        '''
        pass
    
    def set_cdn_container_index(self, container=None, index_file=''):
        '''
            Instructs Cloud Files to use the suppled file name as an index file
            for a CDN enabled container. Returns boolean True on success. 
        '''
        pass
    
    def set_cdn_container_error(self, container=None, error_file=''):
        '''
            Instructs Cloud Files to use the suppled file name as an error file
            for a CDN enabled container for 401 and 404 errors. Returns boolean
            True on success. 
        '''
        pass

'''

    EOF

'''
