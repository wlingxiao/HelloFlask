import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User()
        u.password = 'cat'
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User()
        u.password = 'cat'
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User()
        u.password = 'cat'
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User()
        u.password='cat'
        u2 = User()
        u2.password='cat2'
        self.assertTrue(u.password_hash != u2.password_hash)