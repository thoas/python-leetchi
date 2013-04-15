import os
from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('leetchi').__version__

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(root, 'CHANGES.txt')) as f:
    CHANGES = f.read()

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

KEYWORDS = 'leetchi api rest users wallets contributions'

setup(
    name='python-leetchi',
    version=version,
    description='Leetchi API implementation in Python',
    long_description=README + '\n\n' + CHANGES,
    author='Florent Messa',
    author_email='florent.messa@gmail.com',
    url='http://github.com/thoas/python-leetchi',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'distribute',
        'requests',
        'simplejson>=2.0.9',
        'M2Crypto>=0.21.1',
        'blinker==1.2'
    ],
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    tests_require=['nose', 'coverage', 'selenium'],
    test_suite="nose.collector"
)
