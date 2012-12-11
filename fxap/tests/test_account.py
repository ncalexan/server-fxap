from webtest import TestApp
import unittest
import json
import random

from support import main

random.seed(1000)

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(main({}))
        self.email = "%d@bar.com" % random.randint(1000000, 9999999)

    def test_bad_create(self):
        res = self.app.post('/account/create', status=400)

    def _create(self, email, *args, **kw):
        body = {}
        body['email'] = email
        body['salt'] = 'salt'
        body['S1'] = 'S1'

        res = self.app.post('/account/create', json.dumps(body), *args, **kw)
        return res

    def test_create(self):

        res = self._create(self.email)
        assert res.json['email'] == self.email

    def test_already_used(self):
        res = self._create(self.email)
        assert res.json['email'] == self.email

        self._create(self.email, status=409)

    def test_uk_no_acocunt(self):
        body = {}
        body['email'] = self.email
        body['S1'] = 'S1'

        res = self.app.post('/key/uk/get', json.dumps(body), status=401)

    def test_get_no_uk(self):
        res = self._create(self.email)
        assert res.json['email'] == self.email

        body = {}
        body['email'] = self.email
        body['S1'] = 'S1'

        res = self.app.post('/key/uk/get', json.dumps(body), status=404)

    def test_uk(self):
        KEY = 'uk uk uk'

        res = self._create(self.email)
        assert res.json['email'] == self.email

        body = {}
        body['email'] = self.email
        body['S1'] = 'S1'
        body['key'] = KEY

        res = self.app.post('/key/uk/put', json.dumps(body))

        body = {}
        body['email'] = self.email
        body['S1'] = 'S1'

        res = self.app.post('/key/uk/get', json.dumps(body))
        assert res.json['key'] == KEY
