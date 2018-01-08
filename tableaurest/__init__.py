# -*- coding: utf-8 -*-

"""Tableau REST API interface with misc utilities."""

import logging

from tableaurest.core import TableauREST

__title__ = 'tableaurest'
__version__ = '0.3.0'
__license__ = 'MIT license'
__author__ = 'Levi Kanwischer'
__maintainer__ = 'Levi Kanwischer'
__email__ = 'hello@levibrooks.co'
__all__ = [
    '__title__',
    '__version__',
    'TableauREST',
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
