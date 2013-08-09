#!/usr/bin/env python

import os
from setuptools import setup

docs_require = ['Sphinx']
tests_require = ['nose', 'coverage']

try:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.rst')) as r:
        README = r.read()
except IOError:
    README = ''

setup(name='pheme.anonymize',
      version='13.05',
      description="PHEME module to anonymize syndromic data files",
      long_description=README,
      license="BSD-3 Clause",
      namespace_packages=['pheme'],
      packages=['pheme.anonymize'],
      include_package_data=True,
      install_requires=['setuptools', 'pheme.util', 'hl7'],
      setup_requires=['nose'],
      tests_require=tests_require,
      test_suite="nose.collector",
      extras_require = {'test': tests_require,
                        'docs': docs_require,
                        },
      entry_points=("""
                    [console_scripts]
                    lookup_cached_term=pheme.anonymize.termcache:lookup_term_ep
                    store_cached_term=pheme.anonymize.termcache:store_term_ep
                    anonymize_file=pheme.anonymize.mbds_hl7:anonymize_file
                    """),
)
