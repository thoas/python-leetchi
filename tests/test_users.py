import os
import unittest
import requests

from datetime import date

from .resources import handler, User, StrongAuthentication


class UsersTest(unittest.TestCase):
    def setUp(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'images', 'rib.jpg')

    def test_create_user_with_birthday_lt_1900(self):
        params = {
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'birthday': date(1850, 1, 1),
            'nationality': 'FR',
        }
        user = User(**params)

        self.assertEqual(user.get_pk() is None, True)
        user.save(handler)

        for key, value in params.items():
            self.assertEqual(getattr(user, key), value)

        self.assertEqual(user.get_pk() is None, False)

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

    def test_strong_authentication(self):
        user = User(**{
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'birthday': date.today(),
            'nationality': 'FR',
        })

        user.save(handler)

        auth = StrongAuthentication(user=user, beneficiary_id=0)
        auth.save(handler)

        result = requests.post(auth.url_request, files={
            'StrongValidationDto.Picture': open(self.file_path)
        })

        self.assertEqual(result.status_code, 200)

        strong_authentication = user.strong_authentication

        self.assertEqual(strong_authentication.user, user)

        strong_authentication.is_transmitted = True
        strong_authentication.save()

        user = User(**{
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'birthday': date.today(),
            'nationality': 'FR',
        })
        user.save(handler)

        self.assertRaises(StrongAuthentication.DoesNotExist, user.strong_authentication)

    def test_retrieve_user(self):
        params = {
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'nationality': 'FR',
            'birthday': date(1970, 1, 1)
        }
        user = User(**params)
        user.save(handler)

        self.assertRaises(User.DoesNotExist, User.get, user.get_pk() + 1, handler=handler)

        user = User.get(user.get_pk(), handler=handler)

        self.assertEqual(user.get_pk() is None, False)

        for key, value in params.items():
            self.assertEqual(getattr(user, key), value)
