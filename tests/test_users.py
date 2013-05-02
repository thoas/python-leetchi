import unittest

from datetime import date

from .resources import handler, User


class UsersTest(unittest.TestCase):
    def test_create_user(self):
        params = {
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'birthday': date.today(),
            'nationality': 'FR',
        }
        user = User(**params)

        self.assertEqual(user.get_pk() is None, True)
        user.save(handler)

        for key, value in params.items():
            self.assertEqual(getattr(user, key), value)

        self.assertEqual(user.get_pk() is None, False)

        previous_pk = user.get_pk()

        user.first_name = 'Mike'
        user.save(handler)

        self.assertEqual(previous_pk, user.get_pk())

        self.assertEqual(user.first_name, 'Mike')

    def test_retrieve_user(self):
        params = {
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'nationality': 'FR',
        }
        user = User(**params)
        user.save(handler)

        self.assertRaises(User.DoesNotExist, User.get, user.get_pk() + 1, handler=handler)

        user = User.get(user.get_pk(), handler=handler)

        self.assertEqual(user.get_pk() is None, False)

        for key, value in params.items():
            self.assertEqual(getattr(user, key), value)
