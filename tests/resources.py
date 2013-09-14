import random

from . import settings

from leetchi.api import LeetchiAPI

handler = LeetchiAPI(settings.API_PARTNER_ID,
                     settings.API_PRIVATE_KEY,
                     settings.API_PRIVATE_KEY_PASSWORD,
                     sandbox=settings.API_USE_SANDBOX,
                     host=settings.API_HOST)

from leetchi.resources import *  # noqa


def get_bank_account():
    return API_BANK_ACCOUNTS[random.randint(0, len(API_BANK_ACCOUNTS) - 1)]
