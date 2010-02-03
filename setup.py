# -*- coding: utf-8 -*-
from setuptools import setup
import sys
import unittest

import pyxml2obj
from pyxml2obj import __version__, __license__, __author__

if __name__ == '__main__':
  from pyxml2obj import pyxml2obj_in_test, pyxml2obj_out_test
  # run module test
  loader = unittest.TestLoader()
  result = unittest.TestResult()
  suite  = loader.loadTestsFromModule(pyxml2obj_in_test)
  suite.run(result)
  if not result.wasSuccessful():
    print "unit tests for XMLin have failed!"
    print "aborted to make a source distribution"
    sys.exit(1)
  suite = loader.loadTestsFromModule(pyxml2obj_out_test)
  suite.run(result)
  if not result.wasSuccessful():
    print "unit tests for XMLout have failed!"
    print "aborted to make a source distribution"
    sys.exit(1)
    
  # build distribution package
  setup(
    packages         = ('pyxml2obj',),
    name             = 'pyxml2obj',
    version          = __version__,
    py_modules       = ['pyxml2obj', 'pyxml2obj_in_test', 'pyxml2obj_out_test'],
    description      = 'pyxml2obj convert xml to python object and vice versa. This module is inspired by XML::Simple in CPAN',
    long_description = pyxml2obj.__doc__,
    author           = __author__,
    author_email     = 'taichino@gmail.com',
    url              = 'http://github.com/taichino/pyxml2obj',
    keywords         = 'xml, xml converter, xml to object',
    license          = __license__,
    classifiers      = ["Development Status :: 3 - Alpha",
                        "Intended Audience :: Developers",
                        "License :: OSI Approved :: MIT License",
                        "Operating System :: POSIX",
                        "Programming Language :: Python",
                        "Topic :: Software Development :: Libraries :: Python Modules"]
    )
