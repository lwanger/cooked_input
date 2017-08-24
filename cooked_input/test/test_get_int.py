
"""
pytest tests for cooked_input

Len Wanger, 2017
"""

import sys
from io import StringIO
import pytest

from cooked_input import get_input, IntConvertor, InRangeValidator

from .utils import redirect_stdin


class TestGetInt(object):

    def test_get_int(self):
        test_get_int_str = """
            10
            5
            -1
            1
    
            """

        irv = InRangeValidator(min_val=1, max_val=10)
        with redirect_stdin(StringIO(test_get_int_str)):
            result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
            print(result)
            assert(result==10)

            result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
            print(result)
            assert(result==5)

            result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
            print(result)
            assert(result==1)


    def test_raise_value_exception(self):
        test_raise_value_error_exception_str = """
            foo
            101
            """

        with redirect_stdin(StringIO(test_raise_value_error_exception_str)):
            # with pytest.raises(ValueError):
            result = get_input(prompt='Enter an integer', convertor=IntConvertor())
            assert(result==101)
