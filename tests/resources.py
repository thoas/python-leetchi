import random

from settings import *

from leetchi.api import LeetchiAPI

handler = LeetchiAPI(API_PARTNER_ID, API_PRIVATE_KEY, API_PRIVATE_KEY_PASSWORD, sandbox=API_USE_SANDBOX)

from leetchi.resources import *


def get_bank_account():
    return API_BANK_ACCOUNTS[random.randint(0, len(API_BANK_ACCOUNTS) - 1)]
