
"""
pytest tests for cooked_input

Len Wanger, 2017
"""

import sys
from io import StringIO

from cooked_input import get_input, IntConvertor, InRangeValidator


class redirect_stdin():
    def __init__(self, f):
        self.f = f

    def __enter__(self):
        sys.stdin = self.f

    def __exit__(self, *args):
        sys.stdin = sys.__stdin__

test_get_int_str="""
10
5
-1
1

"""


def test_get_int():
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


test_get_int()
