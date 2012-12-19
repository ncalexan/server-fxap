from zope.interface import Interface


class IAccountServerBackend(Interface):


    def create_account(self, email, salt, S1):
        """Create an account for the given email address."""


    def get_account(self, email):
        """Return the account for the given email address, or None."""


    def get_device_token(self, email):
        """Return new device token for given email address."""


    def is_valid_device_token(self, email, device_token):
        """Return true if device token is valid for given email address."""


    def get_service_token(self, email, service, device_token):
        """Return new service token for given email address and service."""


    def is_valid_service_token(self, email, service_token):
        """Return true if service token is valid for given email address."""
