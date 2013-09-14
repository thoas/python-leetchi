import sys

try:
    from . import credentials
except ImportError as e:
    sys.stderr.write('Error: Can\'t find the file credentials.py')
    raise e

API_PARTNER_ID = getattr(credentials, 'API_PARTNER_ID', 'partnerID')
API_PRIVATE_KEY = getattr(credentials, 'API_PRIVATE_KEY', 'file://path/to/private_key')
API_PRIVATE_KEY_PASSWORD = getattr(credentials, 'API_PRIVATE_KEY_PASSWORD', '$ecret')
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
