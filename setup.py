"""
    setup for tml.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
from setuptools import setup, find_packages

def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''

# Use the docstring of the __init__ file to be the description
DESC = " ".join(__import__('tml').__doc__.splitlines()).strip()

maps = [os.sep.join(('tml/maps', name)) for name in os.listdir('tml/maps')]
mapres = [os.sep.join(('tml/mapres', name)) for name in os.listdir('tml/mapres')]
setup(
    name = "tml",
    version = __import__('tml').get_version().replace(' ', '-'),
    url = '',
    author = 'TML Team',
    author_email = '',
    description = DESC,
    long_description = read_file('README'),
    packages = find_packages(),
    include_package_data = True,
    install_requires=read_file('requirements.txt'),
    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
    data_files=[('tml/maps', maps),
                ('tml/mapres', mapres)]
)
