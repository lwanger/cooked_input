
"""
pytest test utilities for cooked_input

Len Wanger, 2017
"""

import sys
from io import StringIO

from cooked_input import get_input, IntConvertor, InRangeValidator


class redirect_stdin():
    # context manager for redirecting stdin. Usable with "with" keyword
    def __init__(self, f):
        self.f = f

    def __enter__(self):
        sys.stdin = self.f

    def __exit__(self, *args):
        sys.stdin = sys.__stdin__
