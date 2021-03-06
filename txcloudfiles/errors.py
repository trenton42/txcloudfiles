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

    Exceptions raised by txcloudfiles operations.

'''

class CloudFilesException(Exception):
    '''
        Root catchable exception.
    '''
    pass

class InvalidEndpointException(CloudFilesException):
    '''
        The supplied endpoint to connect to is invalid.
    '''
    pass

class NotAuthenticatedException(CloudFilesException):
    '''
        Token cannot be retrieved, not authenticated.
    '''
    pass

class CannotCreateSessionException(CloudFilesException):
    '''
        Unable to create a new authentication session.
    '''

''' transport errors '''

class OperationConfigException(CloudFilesException):
    '''
        An operation is not overriding a required class constant.
    '''
    pass

class CreateRequestException(CloudFilesException):
    '''
        Request could not be created, required parameters missing.
    '''
    pass

class RequestException(CloudFilesException):
    '''
        An error occured in a request.
    '''
    pass

class ResponseException(CloudFilesException):
    '''
        An error occured in a response.
    '''
    pass

'''

    EOF

'''
