from setuptools import setup, find_packages

version = __import__('leetchi').__version__

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
    name='leetchi',
    version=version,
    description='Leetchi API implementation in Python',
    author='Florent Messa',
    author_email='florent.messa@gmail.com',
    url='http://github.com/thoas/python-leetchi',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['distribute', 'requests', 'simplejson>=2.0.9', 'M2Crypto>=0.21.1'],
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    tests_require=['nose', 'coverage', 'selenium'],
    test_suite = "nose.collector"
)
