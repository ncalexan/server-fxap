# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

""" Cornice services.
"""

from cornice import Service
from cornice.errors import Errors
from cornice.util import json_error as cornice_error

import os
import base64
import json

import webob.exc as exc

def json_error(status=400, location='body', name='', description='', **kw):
        errors = Errors(status=status)
        errors.add(location=location, name=name, description=description, **kw)
        return cornice_error(errors)

fxap_reset = Service(name='', path='/fxap/reset', description="Firefox Accounts Protocol Server")
fxap_info = Service(name='', path='/fxap/info', description="Firefox Accounts Protocol Server")

account_create = Service(name='', path='/account/create', description="Firefox Accounts Protocol Server")
account_info = Service(name='', path='/account/info', description="Firefox Accounts Protocol Server")
key_uk_get = Service(name='', path='/key/uk/get', description="Firefox Accounts Protocol Server")
key_uk_put = Service(name='', path='/key/uk/put', description="Firefox Accounts Protocol Server")

token_device_get = Service(name='', path='/token/device/get', description="Firefox Accounts Protocol Server")
token_service_get = Service(name='', path='/token/service/get', description="Firefox Accounts Protocol Server")

_ACCOUNTS = {}
_DEVICE_TOKEN_COUNTER = 10
_SERVICE_TOKEN_COUNTER = 40

def get_device_token(account):
    global _DEVICE_TOKEN_COUNTER

    _DEVICE_TOKEN_COUNTER += 1
    return "device-%s" % _DEVICE_TOKEN_COUNTER

def get_service_token(account, device_token, service):
    global _SERVICE_TOKEN_COUNTER

    _SERVICE_TOKEN_COUNTER += 1
    return "%s-service-%s-%s" % (device_token, service, _SERVICE_TOKEN_COUNTER)

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

@fxap_reset.post(validators=[valid_message, valid_key('password')])
def _(request):
    fxap_password = request.registry.settings.get('fxap.password', None)

    if fxap_password is None:
        return exc.HTTPUnauthorized()

    if request.validated['password'] != fxap_password:
        return exc.HTTPUnauthorized()

    _ACCOUNTS.clear()
    return {}

@fxap_info.post(validators=[valid_message, valid_key('password')])
def _(request):
    fxap_password = request.registry.settings.get('fxap.password', None)

    if fxap_password is None:
        return exc.HTTPUnauthorized()

    if request.validated['password'] != fxap_password:
        return exc.HTTPUnauthorized()

    return {"accounts": str(_ACCOUNTS)}

@account_create.post(validators=[valid_message, valid_key('email'), valid_key('salt'), valid_key('S1')])
def _(request):
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

    if email in _ACCOUNTS:
        request.errors.add('body', 'message', 'email already in use')
        request.errors.status = 409
        return

    _ACCOUNTS[email] = {'email': email, 'salt': salt, 'S1':S1, 'device_tokens':[], 'service_tokens':{}}

    return {'email': email}

def valid_user(request):
    valid_key('email')(request)
    valid_key('S1')(request)

    email = request.validated['email']
    S1 = request.validated['S1']

    if email not in _ACCOUNTS:
        raise exc.HTTPUnauthorized()

    account = _ACCOUNTS[email]

    S1 = request.validated['S1']
    if S1 != account['S1']:
        raise exc.HTTPUnauthorized()

    request.validated['account'] = account

def valid_email(request):
    valid_key('email')(request)

    email = request.validated['email']

    if email not in _ACCOUNTS:
        raise exc.HTTPNotFound()

    account = _ACCOUNTS[email]

    request.validated['account'] = account

@account_info.post(validators=[valid_message, valid_key('email'), valid_email])
def _(request):
    account = request.validated['account']

    return {'email': account['email'],
            'salt': account['salt'] }

@key_uk_put.post(validators=[valid_message, valid_user, valid_key('key')])
def _(request):
    r"""
    """
    account = request.validated['account']
    key = request.validated['key']

    account['uk'] = key

@key_uk_get.post(validators=[valid_message, valid_user])
def _(request):
    r"""
    """
    account = request.validated['account']

    if 'uk' in account:
        return {'key': account['uk']}
    else:
        raise exc.HTTPNotFound()

@token_device_get.post(validators=[valid_message, valid_user])
def _(request):
    r"""
    """
    account = request.validated['account']

    device_token = get_device_token(account)
    account['device_tokens'].append(device_token)

    return {'device_token': device_token}

def valid_device(request):
    valid_key('device_token')(request)

    account = request.validated['account']
    device_token = request.validated['device_token']

    if device_token not in account['device_tokens']:
        raise exc.HTTPUnauthorized()

    request.validated['device_token'] = device_token

@token_service_get.post(validators=[valid_message, valid_email, valid_device, valid_key('service')])
def _(request):
    r"""
    """
    account = request.validated['account']
    service = request.validated['service']
    device_token = request.validated['device_token']

    service_token = get_service_token(account, device_token, service)

    account['service_tokens'][(device_token, service)] = service_token

    return {'service_token': service_token}
