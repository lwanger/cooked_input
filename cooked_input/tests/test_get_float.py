
"""
pytest tests for cooked_input floating point numbers

pytest stuff
    run with:
        pytest cooked_input/

    cmd line args:
        -q <test_file_name>     - run a specific test file
    floating point stuff (https://docs.pytest.org/en/latest/builtin.html?highlight=approx#pytest.approx)
        approx()
    exception raised:
        https://docs.pytest.org/en/latest/getting-started.html#asserting-that-a-certain-exception-is-raised

Len Wanger, 2017
"""

from io import StringIO

from pytest import approx

from cooked_input import get_input, get_float, FloatConvertor
from .utils import redirect_stdin
# from cooked_input.tests.utils import redirect_stdin   # needed this to run under main here


class TestGetFloat(object):
    float_convertor = FloatConvertor()

    def test_get_input_float(self):
        input_str = """
            10
            5.1
            foo
            -1.1
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='enter a float', convertor=self.float_convertor)
            assert(result==approx(10))

            result = get_input(prompt='enter a float', convertor=self.float_convertor)
            assert(result==approx(5.1))

            result = get_input(prompt='enter a float', convertor=self.float_convertor)
            assert(result==approx(-1.1))


    def test_get_float(self):
        input_str = """
            foo
            3.14
            101
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_float()
            assert (result == approx(3.14))

            result = get_float(prompt='Enter an float')
            assert (result == approx(101.0))


# if __name__ == '__main__':
#     c = TestGetFloat()
#     c.test_get_float()