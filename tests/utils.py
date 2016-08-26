import unittest

from web import app


class AbstractTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['WTF_CSRF_ENABLED'] = False
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def login(self, email, password):
        return self.app.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
