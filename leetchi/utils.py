# see: http://hustoknow.blogspot.com/2011/01/m2crypto-and-facebook-python-sdk.html
from __future__ import unicode_literals

import six

from decimal import Decimal

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5

if six.PY3:
    from urllib import request
    orig = request.URLopener.open_https
    request.URLopener.open_https = orig   # uncomment this line back and forth
elif six.PY2:
    import urllib
    orig = urllib.URLopener.open_https
    urllib.URLopener.open_https = orig

import datetime


def openssl_pkey_get_private(filename, password):
    private_key = RSA.importKey(open(filename, 'r').read(), password)

    return private_key


def openssl_sign(data, key):
    h = SHA.new(data.encode('utf-8'))
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)

    return signature


# This code belongs to https://github.com/carljm/django-model-utils
class Choices(object):
    """
    A class to encapsulate handy functionality for lists of choices
    for a Django model field.

    Each argument to ``Choices`` is a choice, represented as either a
    string, a two-tuple, or a three-tuple.

    If a single string is provided, that string is used as the
    database representation of the choice as well as the
    human-readable presentation.

    If a two-tuple is provided, the first item is used as the database
    representation and the second the human-readable presentation.

    If a triple is provided, the first item is the database
    representation, the second a valid Python identifier that can be
    used as a readable label in code, and the third the human-readable
    presentation. This is most useful when the database representation
    must sacrifice readability for some reason: to achieve a specific
    ordering, to use an integer rather than a character field, etc.

    Regardless of what representation of each choice is originally
    given, when iterated over or indexed into, a ``Choices`` object
    behaves as the standard Django choices list of two-tuples.

    If the triple form is used, the Python identifier names can be
    accessed as attributes on the ``Choices`` object, returning the
    database representation. (If the single or two-tuple forms are
    used and the database representation happens to be a valid Python
    identifier, the database representation itself is available as an
    attribute on the ``Choices`` object, returning itself.)

    """

    def __init__(self, *choices):
        self._full = []
        self._choices = []
        self._choice_dict = {}
        for choice in self.equalize(choices):
            self._full.append(choice)
            self._choices.append((choice[0], choice[2]))
            self._choice_dict[choice[1]] = choice[0]

    def equalize(self, choices):
        for choice in choices:
            if isinstance(choice, (list, tuple)):
                if len(choice) == 3:
                    yield choice
                elif len(choice) == 2:
                    yield (choice[0], choice[0], choice[1])
                else:
                    raise ValueError("Choices can't handle a list/tuple of length %s, only 2 or 3"
                                     % len(choice))
            else:
                yield (choice, choice, choice)

    def __len__(self):
        return len(self._choices)

    def __iter__(self):
        return iter(self._choices)

    def __getattr__(self, attname):
        try:
            return self._choice_dict[attname]
        except KeyError:
            raise AttributeError(attname)

    def __getitem__(self, index):
        return self._choices[index]

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join(("%s" % repr(i) for i in self._full)))


def timestamp_from_datetime(dt):
    epoch = datetime.datetime(1970, 1, 1)
    diff = dt - epoch
    return diff.days * 24 * 3600 + diff.seconds


def timestamp_from_date(date):
    epoch = datetime.date(1970, 1, 1)
    diff = date - epoch
    return diff.days * 24 * 3600 + diff.seconds


if six.PY3:
    memoryview = memoryview
else:
    memoryview = buffer


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_text(strings_only=True).
    """
    return isinstance(obj, six.integer_types + (type(None), float, Decimal,
                                                datetime.datetime, datetime.date, datetime.time))


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first, saves 30-40% when s is an instance of
    # six.text_type. This function gets called often in that setting.
    if isinstance(s, six.text_type):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not isinstance(s, six.string_types):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                if six.PY3:
                    if isinstance(s, bytes):
                        s = six.text_type(s, encoding, errors)
                    else:
                        s = six.text_type(s)
                else:
                    s = six.text_type(bytes(s), encoding, errors)
        else:
            # Note: We use .decode() here, instead of six.text_type(s, encoding,
            # errors), so that if s is a SafeBytes, it ends up being a
            # SafeText at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError:
        # If we get to here, the caller has passed in an Exception
        # subclass populated with non-ASCII bytestring data without a
        # working unicode method. Try to handle this without raising a
        # further exception by individually forcing the exception args
        # to unicode.
        s = ' '.join([force_text(arg, encoding, strings_only,
                                 errors) for arg in s])
    return s


def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, memoryview):
        s = bytes(s)
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and (s is None or isinstance(s, int)):
        return s
    if not isinstance(s, six.string_types):
        try:
            if six.PY3:
                return six.text_type(s).encode(encoding)
            else:
                return bytes(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return b' '.join([force_bytes(arg, encoding, strings_only,
                                              errors) for arg in s])
            return six.text_type(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


if six.PY3:
    force_str = force_text
else:
    force_str = force_bytes
