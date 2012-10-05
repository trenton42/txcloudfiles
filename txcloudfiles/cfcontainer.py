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

class ContainerSet(object):
    '''
        An iterable of Container objects.
    '''
    
    def __init__(self, data):
        self._containers = []
        for line in data.split('\n'):
            line = line.strip()
            if line:
                self._containers.append(Container(name=line))
    
    def __repr__(self):
        return '<CloudFiles %s object (%s Containers) at %s>' % (self.__class__.__name__, len(self._containers), hex(id(self)))
    
    def __iter__(self):
        for c in self._containers:
            yield c

class Container(object):
    '''
        A representation of a Cloud Files container.
    '''
    def __init__(self, name=''):
        self._name = name
    
    def __repr__(self):
        return '<CloudFiles %s object (%s) at %s>' % (self.__class__.__name__, self._name, hex(id(self)))
    
    def __unicode__(self):
        return u'%s' % self._name
    
    def __str__(self):
        return self._name

'''

    EOF

'''
