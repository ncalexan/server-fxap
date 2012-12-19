# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.


from cornice.errors import Errors
from cornice.util import json_error as cornice_error


def json_error(status=400, location='body', name='', description='', **kw):
    errors = Errors(status=status)
    errors.add(location=location, name=name, description=description, **kw)
    return cornice_error(errors)
