from webtest import TestApp
import unittest
import json

from support import main

class TestAccount(unittest.TestCase):

    def test_bad_create(self):
        app = TestApp(main({}))
        res = app.post('/account/create', status=400)

    def test_create(self):
        EMAIL = 'foo@bar.com'

        app = TestApp(main({}))

        body = {}
        body['email'] = EMAIL
        body['salt'] = 'salt'
        body['S1'] = 'S1'

        res = app.post('/account/create', json.dumps(body))

        assert res.json['email'] == EMAIL

    def test_already_used(self):
        EMAIL = 'double@bar.com'

        app = TestApp(main({}))

        body = {}
        body['email'] = EMAIL
        body['salt'] = 'salt'
        body['S1'] = 'S1'

        res = app.post('/account/create', json.dumps(body))

        assert res.json['email'] == EMAIL

        app.post('/account/create', json.dumps(body), status=409)
