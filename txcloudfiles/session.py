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
from errors import NotAuthenticatedException
from requests import account, containers, objects, cdn, streaming

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
    
    def __init__(self, username='', key='', storage_url='', cdn_url='', servicenet=''):
        self._timer = time() if key else 0
        self._username = username if username else ''
        self._key = key if key else ''
        self._storage_url = storage_url
        self._cdn_url = cdn_url
        self._storage_url_parts = urlsplit(storage_url)
        self._cdn_url_parts = urlsplit(cdn_url)
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
    
    def get_username(self):
        return self._username
    
    def using_servicenet(self):
        return True if self._servicenet else False
    
    def get_storage_url_parts(self):
        if self._servicenet:
            self._storage_url_parts.netloc = self._servicenet + self._storage_url_parts.netloc
        return self._storage_url_parts
    
    def get_cdn_url_parts(self):
        return self._cdn_url_parts
    
    ''' account requests '''
    
    get_account_metadata = account.get_account_metadata
    set_temp_url_key = account.set_temp_url_key
    
    ''' container requests '''
    
    list_containers = containers.list_containers
    list_all_containers = containers.list_all_containers
    create_container = containers.create_container
    delete_container = containers.delete_container
    get_container_metadata = containers.get_container_metadata
    set_container_metadata = containers.set_container_metadata
    enable_container_logging = containers.enable_container_logging
    disable_container_logging = containers.disable_container_logging
    set_cdn_container_index = containers.set_cdn_container_index
    set_cdn_container_error = containers.set_cdn_container_error
    
    ''' object requests '''
    
    list_objects = objects.list_objects
    list_all_objects = objects.list_all_objects
    retrieve_object = objects.retrieve_object
    create_object = objects.create_object
    delete_object = objects.delete_object
    get_object_metadata = objects.get_object_metadata
    set_object_metadata = objects.set_object_metadata
    copy_object = objects.copy_object
    object_content_type = objects.object_content_type
    
    ''' cdn requests '''
    
    list_cdn_containers = cdn.list_cdn_containers
    enable_cdn_container = cdn.enable_cdn_container
    disable_cdn_container = cdn.disable_cdn_container
    get_cdn_container_metadata = cdn.get_cdn_container_metadata
    set_cdn_container_metadata = cdn.set_cdn_container_metadata
    purge_cdn_object = cdn.purge_cdn_object
    
    
    ''' streaming requests '''
    
    stream_upload = streaming.stream_upload
    stream_download = streaming.stream_download
    
class NullSession(object):
    '''
        A null session is used during authentication when a session has not yet
        been created.
    '''

'''

    EOF

'''
