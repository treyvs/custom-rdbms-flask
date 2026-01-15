"""
rdbms/__init__.py
Package initializer - exports main classes
"""

from rdbms.engine import Database, Column, DataType, Table, Index
from rdbms.storage import StorageManager
from rdbms.parser import SQLParser

__all__ = [
    'Database',
    'Column',
    'DataType',
    'Table',
    'Index',
    'StorageManager',
    'SQLParser'
]

__version__ = '1.0.0'
__author__ = 'Built with AI assistance (Claude)'


