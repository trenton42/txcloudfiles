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

    Provides request structure for authentication operations.

'''

from txcloudfiles.transport import Request, Response

class AuthRequest(Request):
    '''
        Get an authentication token.
    '''
    METHOD = Request.GET
    REQUEST_TYPE = Request.REQUEST_AUTH
    REQUIRED_HEADERS = (
        'X-Auth-User',
        'X-Auth-Key',
    )
    EXPECTED_HEADERS = (
        'X-Storage-Url',
        'X-Cdn-Management-Url',
        'X-Auth-Token',
    )
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response objects for auth are handled in txcloudfiles.auth instead '''

'''

    EOF

'''
