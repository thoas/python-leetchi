import requests
import os
import base64
import time
import logging
import six

from requests.exceptions import ConnectionError

try:
    import simplejson as json
except ImportError:
    import json

from .exceptions import APIError, DecodeError

from .utils import openssl_pkey_get_private, openssl_sign

from .signals import request_finished, request_started, request_error

logger = logging.getLogger('leetchi')


def check_required(required, **kwargs):
    missing_requirements = []
    for requirement in required:
        if not requirement in kwargs:
            missing_requirements.append(requirement)

    if len(missing_requirements):
        raise APIError(None, 'Missing required args: %s' % ', '.join(missing_requirements))


class LeetchiAPI(object):
    sandbox_host = 'http://api-preprod.leetchi.com'
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

    def _auth_signature(self, method, url_path, body, timestamp=None):
        if not timestamp:
            timestamp = time.time()

        url_path += '?ts=%d' % int(timestamp)

        data = self._format_data(method, url_path, body)

        private_key = openssl_pkey_get_private(self.private_key, self.private_key_password)

        signed_data = openssl_sign(data, private_key)

        signature = getattr(base64, 'encodestring', 'encodebytes')(signed_data)

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

        timestamp = time.time()

        signature = self._auth_signature(method, url, data, timestamp)

        if six.PY3:
            signature = signature.decode('utf-8')

        headers = {
            'X-Leetchi-Signature': signature.replace('\n', ''),
            'Content-Type': 'application/json'
        }

        if data:
            data = json.dumps(data)

        url = self._generate_host(url, timestamp)

        logger.info(u'DATA[IN -> %s]\n\t- headers: %s\n\t- content: %s' % (url, headers, data))

        ts = time.time()

        request_started.send(url=url, data=data, headers=headers, method=method)

        try:
            result = requests.request(method, url,
                                      headers=headers,
                                      data=data)
        except ConnectionError as e:
            raise APIError(e.message)

        laps = time.time() - ts

        request_finished.send(url=url,
                              data=data,
                              headers=headers,
                              method=method,
                              result=result,
                              laps=laps)

        logger.info(u'DATA[OUT -> %s][%2.3f seconds]\n\t- status_code: %s\n\t- headers: %s\n\t- content: %s' % (
            url,
            laps,
            result.status_code,
            result.headers,
            result.text if hasattr(result, 'text') else result.content)
        )

        if result.status_code in (requests.codes.BAD_REQUEST, requests.codes.forbidden,
                                  requests.codes.not_allowed, requests.codes.length_required,
                                  requests.codes.server_error):
            self._create_apierror(result, url=url)
        else:
            if result.content:
                try:
                    return result, json.loads(result.content)
                except ValueError:
                    self._create_decodeerror(result, url=url)
            else:
                self._create_decodeerror(result, url=url)

    def _create_apierror(self, result, url=None):
        text = result.text if hasattr(result, 'text') else result.content

        status_code = result.status_code

        headers = result.headers

        logger.error(u'API ERROR: status_code: %s | headers: %s | content: %s' % (status_code,
                                                                                  headers,
                                                                                  text))

        request_error.send(url=url, status_code=status_code, headers=headers)

        try:
            content = result.json()
        except ValueError:
            content = None

        raise APIError(text, code=status_code, content=content)

    def _create_decodeerror(self, result, url=None):

        text = result.text if hasattr(result, 'text') else result.content

        status_code = result.status_code

        headers = result.headers

        logger.error(u'DECODE ERROR: status_code: %s | headers: %s | content: %s' % (status_code,
                                                                                     headers,
                                                                                     text))

        request_error.send(url=url, status_code=status_code, headers=headers)

        try:
            content = result.json()
        except ValueError:
            content = None

        raise DecodeError(text,
                          code=status_code,
                          headers=headers,
                          content=content)
