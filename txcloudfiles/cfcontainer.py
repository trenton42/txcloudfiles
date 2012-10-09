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

    Container objects represent a Cloud Files container. They contain objects.
    Containers must be placed inside an account. A ContainerSet is an object
    that stores an iterable set of Containers.

'''

from helpers import parse_int, parse_url_str, DataUsage
from txcloudfiles.cfobject import Object

class ContainerSet(object):
    '''
        An iterable of Container objects.
    '''
    
    def __init__(self):
        self._containers = []
        self._requests = 0
    
    def add_containers(self, containers):
        self._requests += 1
        for container_data in containers:
            container = Container(
                name=container_data.get('name', ''),
                object_count=parse_int(container_data.get('count', 0)),
                bytes=container_data.get('bytes', 0),
                cdn=container_data.get('cdn_enabled', False),
                logging=container_data.get('log_retention', False),
                ttl=parse_int(container_data.get('ttlparse_bool', 0)),
                cdn_uri=container_data.get('cdn_uri', ''),
                ssl_uri=container_data.get('cdn_ssl_uri', ''),
                stream_uri=container_data.get('cdn_streaming_uri', '')
            )
            if container.is_valid():
                self._containers.append(container)
    
    def __repr__(self):
        return '<CloudFiles %s object (%s containers) at %s>' % (self.__class__.__name__, len(self._containers), hex(id(self)))
    
    def __iter__(self):
        for c in self._containers:
            yield c
    
    def __len__(self):
        return len(self._containers)
    
    def __getitem__(self, i):
        return self._containers[i]
    
    def get_request_count(self):
        return self._requests
    
    def get_last_container(self):
        if len(self._containers) > 0:
            return self._containers[-1]
        return None

class Container(object):
    '''
        A representation of a Cloud Files container.
    '''
    
    def __init__(self, name='', object_count=0, bytes=0, metadata={}, cdn=False, logging=False, ttl=0, cdn_uri='', ssl_uri='', stream_uri=''):
        self._objects = []
        self._requests = 0
        self._name = parse_url_str(name)
        self._object_count = object_count
        self._data = DataUsage(bytes)
        self._metadata = metadata
        self._cdn = cdn
        self._logging = logging
        self._ttl = ttl
        self._cdn_uri = cdn_uri
        self._ssl_uri = ssl_uri
        self._stream_uri = stream_uri
    
    def __repr__(self):
        _state = 'public' if self._cdn else 'private'
        _id = hex(id(self))
        d = (self.__class__.__name__, self._name, self._object_count, self._data.b, _state, _id)
        return '<CloudFiles %s object (%s: %s objects, %s bytes, %s) at %s>' % d
    
    def add_objects(self, objects):
        self._requests += 1
        for object_data in objects:
            obj = Object(
                name=object_data.get('name', ''),
                file_hash=object_data.get('hash', ''),
                bytes=object_data.get('bytes', 0),
                content_type=object_data.get('content_type', ''),
                last_modified=object_data.get('last_modified', '')
            )
            if obj.is_valid():
                self._objects.append(obj)
    
    def __iter__(self):
        for o in self._objects:
            yield o
    
    def __len__(self):
        return len(self._objects)
    
    def __getitem__(self, i):
        return self._objects[i]
    
    def __unicode__(self):
        return u'%s' % self.get_name()
    
    def __str__(self):
        return self.get_name()
    
    def get_name(self):
        return self._name
    
    def get_metadata(self):
        return self._metadata
    
    def get_cdn(self):
        return self._cdn
    
    def get_logging(self):
        return self._logging
    
    def get_ttl(self):
        return self._ttl
    
    def get_cdn_url(self):
        return self._cdn_uri
    
    def get_ssl_url(self):
        return self._ssl_uri
    
    def get_stream_url(self):
        return self._stream_uri
    
    def is_valid(self):
        return True if self._name else False
    
    def get_request_count(self):
        return self._requests
    
    def get_last_object(self):
        if len(self._objects) > 0:
            return self._objects[-1]
        return None

'''

    EOF

'''
