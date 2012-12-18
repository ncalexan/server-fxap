from webtest import TestApp
import unittest
import json
import random

from support import main

random.seed(1000)

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(main({}))
        i = random.randint(1000000, 9999999)
        self.email = "%d@bar.com" % i
        self.salt = "salt-%d" % i
        self.S1 = "S1-%d" % i

    def post(self, uri, json_body, *args, **kw):
        json_body['email'] = self.email
        json_body['S1'] = self.S1
        return self.app.post(uri, json.dumps(json_body), *args, **kw)

    def post_unauth(self, uri, json_body, *args, **kw):
        return self.app.post(uri, json.dumps(json_body), *args, **kw)

    def test_bad_create(self):
        res = self.post('/account/create', {}, status=400)

    def _create(self, *args, **kw):
        body = {}
        body['email'] = self.email
        body['salt'] = self.salt
        body['S1'] = self.S1

        res = self.post_unauth('/account/create', body, *args, **kw)
        return res

    def test_create(self):
        res = self._create()
        assert res.json['email'] == self.email

    def test_info(self):
        body = {}
        body['email'] = self.email

        res = self.post_unauth('/account/info', body, status=404)

        res = self._create()
        assert res.json['email'] == self.email

        res = self.post_unauth('/account/info', body)
        assert res.json['salt'] == self.salt

    def test_already_used(self):
        res = self._create()
        assert res.json['email'] == self.email

        self._create(status=409)

    def test_bad_auth(self):
        res = self._create()
        assert res.json['email'] == self.email

        body = {}
        body['email'] = self.email
        body['S1'] = 'BAD S1 VALUE'

        res = self.post_unauth('/key/uk/get', body, status=401)

    def test_uk_no_account(self):
        res = self.post('/key/uk/get', {}, status=401)

    def test_get_no_uk(self):
        res = self._create()
        assert res.json['email'] == self.email

        res = self.post('/key/uk/get', {}, status=404)

    def test_uk(self):
        KEY = 'uk uk uk'

        res = self._create()
        assert res.json['email'] == self.email

        body = {}
        body['key'] = KEY

        res = self.post('/key/uk/put', body)

        res = self.post('/key/uk/get', {})
        assert res.json['key'] == KEY

    def _device(self, *args, **kw):
        res = self.post('/token/device/get', {}, *args, **kw)
        return res

    def test_get_device(self):
        res = self._create()
        assert res.json['email'] == self.email

        res = self._device()
        assert 'device_token' in res.json

    def _service(self, device_token, service, *args, **kw):
        body = {}
        body['device_token'] = device_token
        body['service'] = service

        res = self.post('/token/service/get', body, *args, **kw)
        return res

    def test_get_service(self):
        res = self._create()
        assert res.json['email'] == self.email

        res = self._device()
        assert 'device_token' in res.json
        device_token = res.json['device_token']

        res = self._service(device_token, 'sync')
        assert 'service_token' in res.json
        service_token = res.json['service_token']

    def test_get_service_bad_device_token(self):
        res = self._create()
        assert res.json['email'] == self.email

        bad_device_token = 'BAD DEVICE TOKEN'

        res = self._service(bad_device_token, 'sync', status=401)

    def test_get_sync_token(self):
        res = self._create()
        assert res.json['email'] == self.email

        res = self._device()
        assert 'device_token' in res.json
        device_token = res.json['device_token']

        res = self._service(device_token, 'sync')
        assert 'service_token' in res.json
        service_token = res.json['service_token']

        body = {}
        body['email'] = self.email
        body['service'] = 'sync'
        body['service_token'] = service_token

        res = self.post_unauth('/token/sync/get', body)

        print res.json
        assert str(res.json) == ""
