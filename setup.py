#!/usr/bin/env python
# Licensed under a MIT style license - see LICENSE.rst.

# NOTE: The configuration for the package, including the name, version, and
# other information are set in the setup.cfg file.

import sys
from setuptools import setup

# First provide helpful messages if contributors try and run legacy commands
# for tests or docs.

TEST_HELP = """
Note: running tests is no longer done using 'python setup.py test'. Instead
you will need to run:

    pytest

If you don't already have pytest installed, you can install it with:

    pip install pytest
"""

DOCS_HELP = """
Note: building the documentation is no longer done using
'python setup.py {0}'. Instead you will need to run:

    sphinx-build -W --keep-going -b html docs docs/_build/html

If you don't already have Sphinx installed, you can install it with:

    pip install Sphinx
"""

message = {'test': TEST_HELP,
           'build_docs': DOCS_HELP.format('build_docs'),
           'build_sphinx': DOCS_HELP.format('build_sphinx'), }

for m in message:
    if m in sys.argv:
        print(message[m])
        sys.exit(1)

setup()
