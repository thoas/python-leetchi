import sys

try:
    from . import credentials
except ImportError as e:
    sys.stderr.write('Error: Can\'t find the file credentials.py')
    raise e

API_PARTNER_ID = getattr(credentials, 'API_PARTNER_ID', None)
API_PRIVATE_KEY = getattr(credentials, 'API_PRIVATE_KEY', None)
API_PRIVATE_KEY_PATH = getattr(credentials, 'API_PRIVATE_KEY_PATH', None)
API_PRIVATE_KEY_PASSWORD = getattr(credentials, 'API_PRIVATE_KEY_PASSWORD', None)
API_USE_SANDBOX = getattr(credentials, 'API_USE_SANDBOX', True)
API_HOST = getattr(credentials, 'API_HOST', None)
API_BANK_ACCOUNTS = getattr(credentials, 'API_BANK_ACCOUNTS', [
    {
        'number': 'XXXXXXXXXXXXXXXX',
        'expiration': {
            'year': 'XX',
            'month': 'XX'
        },
        'cvv': 'XXX'
    },
])
