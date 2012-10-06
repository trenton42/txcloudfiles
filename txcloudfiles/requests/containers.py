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

from txcloudfiles.transport import Request, Response

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

'''

    EOF

'''
