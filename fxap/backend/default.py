from collections import defaultdict
import os

def random_guid():
    return os.urandom(10).encode("hex")

from pyramid.threadlocal import get_current_registry
from zope.interface import implements
from fxap.backend import IAccountServerBackend

from mozsvc.exceptions import BackendError

# very basic in memory implementation of user to node assignation. This should
# be done in a persistant way instead.
# _USERS_UIDS = defaultdict(dict)
# _UID = 0

_ACCOUNTS = defaultdict(dict)
_DEVICE_TOKENS = defaultdict(list)
_SERVICE_TOKENS = defaultdict(lambda: defaultdict(dict))

class DefaultAccountServerBackend(object):
    """Dead simple backend keeping everything in memory.
    """
    implements(IAccountServerBackend)


    def __init__(self, **kw):
        pass



# _DEVICE_TOKEN_COUNTER = 10
# _SERVICE_TOKEN_COUNTER = 40

# def get_device_token(account):
#     global _DEVICE_TOKEN_COUNTER

#     _DEVICE_TOKEN_COUNTER += 1
#     return "device-%s" % _DEVICE_TOKEN_COUNTER

# def get_service_token(account, device_token, service):
#     global _SERVICE_TOKEN_COUNTER

#     _SERVICE_TOKEN_COUNTER += 1
#     return "%s-service-%s-%s" % (device_token, service, _SERVICE_TOKEN_COUNTER)

    def _device_token(self, email):
        return random_guid()


    def _service_token(self, email, service, device_token):
        return random_guid()


    def create_account(self, email, salt, S1):
        """Create an account for the given email address."""

        if self.get_account(email) is not None:
            raise BackendError("email address already in use")

        _ACCOUNTS[email] = {'email': email,
                            'salt': salt,
                            'S1': S1}


    def get_account(self, email):
        """Return the account for the given email address, or None."""

        return _ACCOUNTS.get(email)


    def get_device_token(self, email):
        """Return new device token for given email address."""

        device_token = self._device_token(email)
        _DEVICE_TOKENS[email].append(device_token)

        return device_token

    def is_valid_device_token(self, email, device_token):
        """Return true if device token is valid for given email address."""

        return device_token in _DEVICE_TOKENS[email]


    def get_service_token(self, email, service, device_token):
        """Return new service token for given email address and service."""

        service_token = self._service_token(email, service, device_token)
        _SERVICE_TOKENS[email][service][service_token] = device_token

        return service_token

    def is_valid_service_token(self, email, service, service_token):
        """Return true if service token is valid for given email address."""

        return _SERVICE_TOKENS[email][service].get(service_token) in _DEVICE_TOKENS[email]
