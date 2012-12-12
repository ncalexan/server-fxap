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

    def test_already_used(self):
        res = self._create()
        assert res.json['email'] == self.email

        self._create(status=409)

    def test_uk_no_acocunt(self):
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
