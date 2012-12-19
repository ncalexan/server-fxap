# -*- tab-width: 4 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

""" Cornice services.
"""

from cornice import Service
from cornice.errors import Errors
from cornice.util import json_error as cornice_error

from mozsvc.metrics import MetricsService
from mozsvc.exceptions import BackendError

import os
import base64
import json

import webob.exc as exc

from backend import IAccountServerBackend

def json_error(status=400, location='body', name='', description='', **kw):
    errors = Errors(status=status)
    errors.add(location=location, name=name, description=description, **kw)
    return cornice_error(errors)

fxap_reset = MetricsService(name='', path='/fxap/reset', description="Firefox Accounts Protocol Server")
fxap_info = MetricsService(name='', path='/fxap/info', description="Firefox Accounts Protocol Server")

account_create = MetricsService(name='', path='/account/create', description="Firefox Accounts Protocol Server")
account_info = MetricsService(name='', path='/account/info', description="Firefox Accounts Protocol Server")
key_uk_get = MetricsService(name='', path='/key/uk/get', description="Firefox Accounts Protocol Server")
key_uk_put = MetricsService(name='', path='/key/uk/put', description="Firefox Accounts Protocol Server")

token_device_get = MetricsService(name='', path='/token/device/get', description="Firefox Accounts Protocol Server")
token_service_get = MetricsService(name='', path='/token/service/get', description="Firefox Accounts Protocol Server")

token_sync_get = MetricsService(name='', path='/token/sync/get', description="Firefox Accounts Protocol Server")

def valid_message(request):
    try:
        message = json.loads(request.body)
    except ValueError:
        raise json_error(description='Not valid JSON')

    request.validated['message'] = message

def valid_key(key):
    def _valid_key(request):
        message = request.validated['message']

        try:
            request.validated[key] = message[key]
        except KeyError:
            raise json_error(description='%s parameter is required' % key)

    return _valid_key

# @fxap_reset.post(validators=[valid_message, valid_key('password')])
# def _fxap_reset(request):
#     fxap_password = request.registry.settings.get('fxap.password', None)

#     if fxap_password is None:
#         return exc.HTTPUnauthorized()

#     if request.validated['password'] != fxap_password:
#         return exc.HTTPUnauthorized()

#     _ACCOUNTS.clear()
#     return {"accounts": _ACCOUNTS}

# @fxap_info.post(validators=[valid_message, valid_key('password')])
# def _fxap_info(request):
#     fxap_password = request.registry.settings.get('fxap.password', None)

#     if fxap_password is None:
#         return exc.HTTPUnauthorized()

#     if request.validated['password'] != fxap_password:
#         return exc.HTTPUnauthorized()

#     return {"accounts": _ACCOUNTS}

@account_create.post(validators=[valid_message, valid_key('email'), valid_key('salt'), valid_key('S1')])
def _account_create(request):
    r"""/api/create_account

Request parameters:

    email : unicode string
    salt : base32-encoded binary salt string
    S1 : base64-encoded binary authorization string

Responses:

    200 OK, {userid: (printable string) }
    409 CONFLICT, "email already in use"
    400 BAD REQUEST, "malformed email address"
"""
    email = request.validated['email']
    salt = request.validated['salt']
    S1 = request.validated['S1']

    backend = request.registry.getUtility(IAccountServerBackend)

    try:
        backend.create_account(email, salt, S1)
    except BackendError as e:
        raise json_error(409, description=e.msg)

    return {'email': email}

def valid_user(request):
    valid_key('email')(request)
    valid_key('S1')(request)

    email = request.validated['email']
    S1 = request.validated['S1']

    backend = request.registry.getUtility(IAccountServerBackend)

    account = backend.get_account(email)
    if account is None:
        raise json_error(404, description="account not found")

    S1 = request.validated['S1']
    if S1 != account['S1']:
        raise exc.HTTPUnauthorized()

    request.validated['account'] = account

def valid_email(request):
    valid_key('email')(request)

    email = request.validated['email']

    backend = request.registry.getUtility(IAccountServerBackend)

    account = backend.get_account(email)
    if account is None:
        raise json_error(404, description="account not found")

    request.validated['account'] = account

@account_info.post(validators=[valid_message, valid_email])
def get_account_info(request):
    account = request.validated['account']

    return {'email': account['email'],
            'salt': account['salt'] }

@key_uk_put.post(validators=[valid_message, valid_user, valid_key('key')])
def _key_uk_put(request):
    r"""
    """
    account = request.validated['account']
    key = request.validated['key']

    account['uk'] = key

@key_uk_get.post(validators=[valid_message, valid_user])
def _key_uk_get(request):
    r"""
    """
    account = request.validated['account']

    if 'uk' in account:
        return {'key': account['uk']}
    else:
        raise exc.HTTPNotFound()

@token_device_get.post(validators=[valid_message, valid_user])
def _token_device_get(request):
    r"""
    """
    account = request.validated['account']

    backend = request.registry.getUtility(IAccountServerBackend)

    device_token = backend.get_device_token(account['email'])

    return {'device_token': device_token}

def valid_device_token(request):
    valid_key('device_token')(request)

    account = request.validated['account']
    device_token = request.validated['device_token']

    backend = request.registry.getUtility(IAccountServerBackend)

    if not backend.is_valid_device_token(account['email'], device_token):
        raise json_error(401, 'bad device token')

    request.validated['device_token'] = device_token

@token_service_get.post(validators=[valid_message, valid_email, valid_device_token, valid_key('service')])
def _token_service_get(request):
    r"""
    """
    account = request.validated['account']
    service = request.validated['service']
    device_token = request.validated['device_token']

    backend = request.registry.getUtility(IAccountServerBackend)

    service_token = backend.get_service_token(account['email'], service, device_token)

    return {'service_token': service_token}

def valid_service_token(request):
    valid_key('service_token')(request)
    valid_key('service')(request)

    account = request.validated['account']
    service = request.validated['service']
    service_token = request.validated['service_token']

    service_tokens = account['service_tokens']
    if not service_tokens.has_key(service):
        raise exc.HTTPNotFound("service not authorized")

    fetched_service_tokens = service_tokens[service]
    if not fetched_service_tokens.has_key(service_token):
        raise exc.HTTPNotFound("service token not authorized")

    device_token = fetched_service_tokens[service_token]['device_token']
    if device_token not in account['device_tokens']:
        raise exc.HTTPUnauthorized("device token not authorized")

    request.validated['service_token'] = service_token
    request.validated['device_token'] = device_token

@token_sync_get.post(validators=[valid_message, valid_email, valid_service_token])
def _token_sync_get(request):
    r"""
    """
    service_token = request.validated['service']
    service_token = request.validated['service_token']
    device_token = request.validated['device_token']

    return {"service_token": service_token,
            "device_token": device_token}
