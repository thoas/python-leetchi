import time
import unittest

from .resources import handler

try:
    import simplejson as json
except ImportError:
    import json

from .settings import API_PARTNER_ID


class ApiTest(unittest.TestCase):
    def test_generate_host(self):
        timestamp = int(time.time())

        self.assertEqual(handler._generate_host('/users/'),
                         '%(host)s/v1/partner/%(partner_id)s/users/?ts=%(timestamp)s' % {
                             'host': handler.host,
                             'partner_id': API_PARTNER_ID,
                             'timestamp': timestamp
                         })

    def test_generate_api_url(self):
        self.assertEqual(handler._generate_api_url('/users/'),
                         '/v1/partner/%(partner_id)s/users/' % {
                             'partner_id': API_PARTNER_ID
                         })

    def test_format_data(self):
        data = {
            'FirstName': 'Mark',
            'LastName': 'Zuckerberg',
            'Email': 'mark@leetchi.com',
            'IP': '127.0.0.1',
        }

        self.assertEqual(handler._format_data('POST', '/users/', data),
                         'POST|/v1/partner/%(partner_id)s/users/|%(data)s|' % {
                             'data': json.dumps(data),
                             'partner_id': API_PARTNER_ID
                         })
