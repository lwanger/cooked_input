
"""
pytest tests for cooked_input cleaning functions

Len Wanger, 2017
"""

import pytest
from io import StringIO

from pytest import approx

from cooked_input import get_input
from cooked_input import Cleaner, RemoveCleaner
from .utils import redirect_stdin


class TestGetFloat(object):

    def test_call_abstract(self):
        c = Cleaner()
        c(10)

    def test_bad_cleaner(self):
        input_str = 'foo'
        with pytest.raises(RuntimeError):
            with redirect_stdin(StringIO(input_str)):
                result = get_input(cleaners=10)


    def test_remove_cleaner(self):
        input_str = 'foo is bar'
        rc = RemoveCleaner(patterns=['is', u'bar'])
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=rc)
            assert(result == 'foo  ')

        print(rc)

        rc = RemoveCleaner(patterns=['is', b'bar'])
        with pytest.raises(TypeError):
            with redirect_stdin(StringIO(input_str)):
                result = get_input(cleaners=rc)


