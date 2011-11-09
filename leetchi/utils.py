# see: http://hustoknow.blogspot.com/2011/01/m2crypto-and-facebook-python-sdk.html
import urllib
orig = urllib.URLopener.open_https
import M2Crypto.m2urllib
urllib.URLopener.open_https = orig   # uncomment this line back and forth
from M2Crypto import EVP

def openssl_pkey_get_private(filename, password):
    private_key = EVP.load_key(filename, lambda x: password)

    return private_key

def openssl_sign(data, key):
    key.sign_init()
    key.sign_update(data)

    return key.sign_final()
