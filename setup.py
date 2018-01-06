# -*- coding: utf-8 -*-

"""A Python based Tableau REST API interface."""

import codecs
import os
import re

import setuptools

NAME = 'tableaurest'
HERE = os.path.dirname(os.path.abspath(__file__))


def read(filename, source=HERE, package=NAME):
    """Read 'package' file contents from 'source' directory."""
    filepath = os.path.join(source, filename)

    if not os.path.isfile(filepath):
        raise IOError('%s missing from `%s`.' % (filename, package))

    with codecs.open(filepath, encoding='utf-8') as infile:
        contents = infile.read()

    return contents


def read_package_init(package=NAME):
    """Load 'package' `__init__` contents into memory."""
    filepath = os.path.join(package, '__init__.py')
    contents = read(filepath)
    return contents


CONTENTS = read_package_init()


def extract_package_metadata(attribute, contents=CONTENTS):
    """Extract 'attribute' metadata from 'contents'."""
    regex = r'''__%s__\s*=\s*['\"\[]([^'\"]*)['\"\]]''' % attribute

    match = re.search(regex, contents, re.M)  # pylint: disable=no-member
    result = match.group(1) if match else None

    if result is None:
        raise IndexError('`__%s__` missing from package contents.' % attribute)

    return result


def build_package_description(*filenames):
    """Merge file contents into single 'long description'."""
    description = '%s\n%s\n' % (__doc__, '=' * len(__doc__))

    for filename in filenames:
        contents = read(filename)
        description = '%s\n%s\n' % (description, contents)

    return description


setuptools.setup(
    name=NAME,

    version=extract_package_metadata('version'),
    license=extract_package_metadata('license'),

    author=extract_package_metadata('author'),
    author_email=extract_package_metadata('email'),

    maintainer=extract_package_metadata('maintainer'),
    maintainer_email=extract_package_metadata('email'),

    description=__doc__,
    long_description=build_package_description('README.rst', 'CHANGELOG.rst'),
    keywords=[
        'Tableau',
        'Tableau REST API',
        'TabCMD',
    ],

    packages=setuptools.find_packages(
        exclude=['tests', 'examples', ]
    ),

    python_requires='>=3.6',

    install_requires=[
        'click',
        'requests',
    ],
    extras_require={
        'dev': ['flake8', 'pylint', ]
    },

    include_package_data=True,
    package_data={
        NAME: [
        ],
    },

    entry_points={
        'console_scripts': [
            '%s = %s.cli:main' % (NAME, NAME),
        ],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
