import requests
import os
import base64
import time
import logging

try:
    import simplejson as json
except ImportError:
    import json

from .exceptions import APIError, DecodeError

from .utils import openssl_pkey_get_private, openssl_sign

logger = logging.getLogger('leetchi')


def check_required(required, **kwargs):
    missing_requirements = []
    for requirement in required:
        if not requirement in kwargs:
            missing_requirements.append(requirement)

    if len(missing_requirements):
        raise APIError(None, 'Missing required args: %s' % ', '.join(missing_requirements))


class LeetchiAPI(object):
    sandbox_host = 'http://api.prod.leetchi.com'
    production_host = 'http://api.leetchi.com'

    def __init__(self, partner_id, private_key, private_key_password, sandbox=False, host=None):
        self.partner_id = partner_id

        if not os.path.exists(private_key):
            raise Exception('Private key (%s) does not exist' % private_key)

        self.private_key = private_key
        self.private_key_password = private_key_password

        if not host:
            if sandbox:
                self.host = self.sandbox_host
            else:
                self.host = self.production_host
        else:
            self.host = host

    def _auth_signature(self, method, url_path, body):
        url_path += '?ts=%d' % int(time.time())

        data = self._format_data(method, url_path, body)

        private_key = openssl_pkey_get_private(self.private_key, self.private_key_password)

        signed_data = openssl_sign(data, private_key)

        signature = base64.encodestring(signed_data)

        return signature

    def _format_data(self, method, url_path, body):
        data = '%s|%s|' % (method, self._generate_api_url(url_path))

        if method != 'GET':
            data += '%s|' % json.dumps(body)

        return data

    def _generate_host(self, url, timestamp=None):
        if not timestamp:
            timestamp = int(time.time())

        return '%s%s' % (self.host, self._generate_api_url(url)) + '?ts=%d' % timestamp

    def _generate_api_url(self, request_uri):
        return '/v1/partner/%s%s' % (self.partner_id, request_uri)

    def request(self, method, url, data=None):
        headers = {
            'X-Leetchi-Signature': self._auth_signature(method, url, data).replace('\n', ''),
            'Content-Type': 'application/json'
        }

        if data:
            data = json.dumps(data)

        url = self._generate_host(url)

        logger.info(u'DATA[in -> %s]: %s' % (url, data))

        result = requests.request(method, url,
                                  headers=headers,
                                  data=data)

        logger.info(u'DATA[out -> %s]: %s' % (url, result.content))

        if result.content:
            try:
                return result, json.loads(result.content)
            except ValueError:
                self._error(result)
        else:
            self._error(result)

    def _error(self, result):
        logger.error(u'DECODE ERROR: status_code: %s | headers: %s | content: %s' % (result.status_code,
                                                                                     result.headers,
                                                                                     result.content))
        raise DecodeError(result.status_code, result.headers, result.content)
