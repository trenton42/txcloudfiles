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

    Provides request structure for account-wide operations.

'''

from twisted.internet.defer import Deferred
from txcloudfiles.transport import Request, Response
from txcloudfiles.errors import NotAuthenticatedException, RequestException
from txcloudfiles.helpers import parse_int, parse_str
from txcloudfiles.cfaccount import Account

''' requests '''

class AccountMetadataRequest(Request):
    '''
        Get account information request.
    '''
    METHOD = Request.HEAD
    REQUIRED_HEADERS = ()
    REQUIRED_BODY = False
    EXPECTED_HEADERS = (
        'X-Account-Container-Count',
        'X-Account-Bytes-Used',
    )
    EXPECTED_BODY = False
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

class AccountSetTempURLKeyRequest(Request):
    '''
        Set a temporary URL key for an account.
    '''
    METHOD = Request.POST
    REQUIRED_HEADERS = (
        'X-Account-Meta-Temp-Url-Key',
    )
    REQUIRED_BODY = False
    EXPECTED_HEADERS = ()
    EXPECTED_BODY = False
    EXPECTED_RESPONSE_CODE = Response.HTTP_SUCCESSFUL

''' response object wrappers '''

def get_account_metadata(session):
    '''
        Returns an Account() object populated with metadata on success.
    '''
    d = Deferred()
    def _parse(r):
        if r.OK:
            a = Account(session.get_username())
            a.set_container_count(r.headers.get('X-Account-Container-Count', ''))
            a.set_bytes_used(r.headers.get('X-Account-Bytes-Used', ''))
            d.callback(a)
        elif r.status_code == 401:
            d.errback(NotAuthenticatedException('failed to get account information, not authorised'))
        else:
            d.errback(RequestException('failed to get account information'))
    request = AccountMetadataRequest(session)
    request.set_parser(_parse)
    request.run()
    return d

def set_temp_url_key(session, key):
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
    request = AccountSetTempURLKeyRequest(session)
    request.set_header(('X-Account-Meta-Temp-Url-Key', key))
    request.set_parser(_parse)
    request.run()
    return d

'''

    EOF

'''
