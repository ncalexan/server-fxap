# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

""" Cornice services.
"""
from cornice import Service

import os
import base64
import json

from webob.exc import HTTPError

import crypto

get_entropy = Service(name='entropy', path='/api/get_entropy', description="Firefox Accounts Protocol Server")
create_account = Service(name='create_account', path='/api/create_account', description="Firefox Accounts Protocol Server")
sign_key = Service(name='create_account', path='/api/sign_key', description="Firefox Accounts Protocol Server")

@get_entropy.post()
def _(request):
    r"""     
/api/get_entropy

Request parameters: none

Responses:

200 OK, {entropy: (base-64 encoded 32-byte random string)}"""

    randoms = os.urandom(32)
    entropy = base64.standard_b64encode(randoms)

    return {'entropy': entropy}

def has_query(param):
    def has(request):
        if not param in request.GET:
            request.errors.add('query', param,
                               '%s parameter is required' % param)
        else:
            request.validated[param] = request.GET[param]

    return has


class _409(HTTPError):
    def __init__(self, msg='email already in use'):
        body = {'status': 409, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 409
        self.content_type = 'application/json'

_ACCOUNTS = {}

# def valid_email_address(request):
#     email = request.validated['email']
#     if False:
#         # testing for this is hard and probably a bad idea
#         request.errors.add('query', 'email',
#                            'malformed email address')

# def unique_account(request):
#     email = request.validated['email']
#     if email in _ACCOUNTS:
#         raise _409()

def valid_create_account(request):
    try:
        message = json.loads(request.body)
    except ValueError:
        request.errors.add('body', 'message', 'Not valid JSON')
        return

    fail = False
    for key in ['email', 'salt', 'S1']:
        try:
            message[key]
        except KeyError:
            fail = True
            request.errors.add('body', 'message', '%s parameter is required' % key)

    if fail:
        return

    email = str(message['email'])

    try:
        salt = base64.b32decode(message['salt'].encode("utf-8"))
    except:
        request.errors.add('body', 'message', 'invalid salt encoding')
        return

    try:
        S1 = base64.urlsafe_b64decode(message['S1'].encode("utf-8"))
    except:
        request.errors.add('body', 'message', 'invalid S1 encoding')
        return

    request.validated['email'] = email
    request.validated['salt'] = salt
    request.validated['S1'] = S1
    
@create_account.post(validators=[valid_create_account])
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

    _ACCOUNTS[email] = {'salt': salt, 'S1':S1}

    return {'email': email}

def valid_sign_key(request):
    try:
        message = json.loads(request.body)
    except ValueError:
        request.errors.add('body', 'message', 'Not valid JSON')
        return

    fail = False
    for key in ['email', 'S1', 'pubkey']:
        try:
            message[key]
        except KeyError:
            fail = True
            request.errors.add('body', 'message', '%s parameter is required' % key)

    if fail:
        return

    email = str(message['email'])
    pubkey = str(message['pubkey'])

    try:
        S1 = base64.urlsafe_b64decode(message['S1'].encode("utf-8"))
    except:
        request.errors.add('body', 'message', 'invalid S1 encoding')
        return

    request.validated['email'] = email
    request.validated['pubkey'] = pubkey
    request.validated['S1'] = S1

@sign_key.post(validators=[valid_sign_key])
def _(request):
    r"""
/api/sign_key

Request parameters:

    email : unicode string
    S1: base-64 encoded binary string
    pubkey: printable representation of public key (JWK?)

Responses:

    200 OK, {cert: (printable representation of signed key)}
    401 UNAUTHORIZED, "bad authorization string"
    404 NOT FOUND, "unknown email address
    400 BAD REQUEST, "malformed public key"
"""
    email = request.validated['email']
    pubkey = request.validated['pubkey']
    S1 = request.validated['S1']

    # try:
    #     account = _ACCOUNTS[email]
    # except KeyError:
    #     request.errors.add('body', 'message', 'unknown email address')
    #     request.errors.status = 404
    #     return

    # if S1 != account['S1']:
    #     request.errors.add('body', 'message', 'bad authorization string')
    #     request.errors.status = 401
    #     return

    # salt = account['S1']

    certificate = crypto.make_certificate(email, pubkey, "mockmyid.com", crypto.MOCKMYID_KEY)

    return {'email': email,
            # 'salt': salt,
            'certificate':certificate}
