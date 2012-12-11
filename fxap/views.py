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

from webob.exc import HTTPError

def json_error(status=400, location='body', name='', description='', **kw):
        errors = Errors(status=status)
        errors.add(location=location, name=name, description=description, **kw)
        return cornice_error(errors)

create_account = Service(name='', path='/account/create', description="Firefox Accounts Protocol Server")

_ACCOUNTS = {}

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

@create_account.post(validators=[valid_message, valid_key('email'), valid_key('salt'), valid_key('S1')])
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
