#!/usr/bin/env python
# Licensed under a MIT style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function
#
# Standard imports
#
import glob
import os
import sys
from importlib import import_module
#
# setuptools' sdist command ignores MANIFEST.in
#
from distutils.command.sdist import sdist as DistutilsSdist
from setuptools import setup, find_packages
#
# Begin setup
#
setup_keywords = dict()
setup_keywords['name'] = 'digestor'
setup_keywords['description'] = 'Scripts and metadata for loading survey data into the Data Lab database.'
setup_keywords['author'] = "NSF's OIR Lab Data Lab Project"
setup_keywords['author_email'] = 'datalab@noao.edu'
setup_keywords['license'] = 'MIT'
setup_keywords['url'] = 'https://github.com/noaodatalab/digestor'
# setup_keywords['version'] = '0.2.0.dev82'
#
# Get version from __init__.py.
#
sys.path.insert(0, os.path.abspath('.'))
package = import_module(setup_keywords['name'])
setup_keywords['version'] = package.__version__
#
# Use README.rst as long_description.
#
setup_keywords['long_description'] = ''
if os.path.exists('README.rst'):
    with open('README.rst') as readme:
        setup_keywords['long_description'] = readme.read()
#
# Set other keywords for the setup function.  These are automated, & should
# be left alone unless you are an expert.
#
# Treat everything in bin/ except *.rst as a script to be installed.
#
if os.path.isdir('bin'):
    setup_keywords['scripts'] = [fname for fname in glob.glob(os.path.join('bin', '*'))
                                 if not os.path.basename(fname).endswith('.rst')]
setup_keywords['provides'] = [setup_keywords['name']]
setup_keywords['requires'] = ['Python (>2.7.0)']
# setup_keywords['install_requires'] = ['Python (>2.7.0)']
setup_keywords['zip_safe'] = False
setup_keywords['use_2to3'] = False
setup_keywords['packages'] = find_packages()
# setup_keywords['package_dir'] = {'':'py'}
# setup_keywords['cmdclass'] = {'module_file': DesiModule, 'version': DesiVersion, 'test': DesiTest, 'sdist': DistutilsSdist}
setup_keywords['cmdclass'] = {'sdist': DistutilsSdist}
setup_keywords['test_suite'] = '{name}.test.{name}_test_suite'.format(**setup_keywords)
#
# Autogenerate command-line scripts.
#
setup_keywords['entry_points'] = {'console_scripts': ['sdss2dl = digestor.sdss:main',
                                                      'add_view_metadata = digestor.view:main']}
#
# Add internal data directories.
#
setup_keywords['package_data'] = {'digestor': ['data/*'], }
#                                   'digestor.test': ['t/*']}
#
# Run setup command.
#
setup(**setup_keywords)
