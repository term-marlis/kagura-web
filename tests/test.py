import unittest

from tests.utils import AbstractTestCase


class PeachWebTestCase(AbstractTestCase):
    def test_not_found(self):
        rv = self.app.get('/hoge', follow_redirects=True)
        assert rv.status == '404 NOT FOUND'

    def test_unauthorized(self):
        rv = self.app.get('/profile', follow_redirects=True)
        assert rv.status == '200 OK'
        assert 'Login' in str(rv.data)

    def test_show_user_profile(self):
        self.login('user@example.com', 'password')
        rv = self.app.get('/profile', follow_redirects=True)
        assert rv.status == '200 OK'
        assert 'Profile' in str(rv.data)


if __name__ == '__main__':
    unittest.main()
