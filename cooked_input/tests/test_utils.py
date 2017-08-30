
"""
pytest tests for cooked_input: test the utility functions

Len Wanger, 2017
"""

from cooked_input.input_utils import compose, put_in_a_list

class TestUtils(object):

    def a(self, value):
        return value + 1

    def b(self, value):
        return value * 2

    def c(self, value):
        return str('result is: {}'.format(value))

    def test_compose(self):
        # test compose function
        result = compose(4, funcs=[self.a, self.b, self.c])
        assert(result == 'result is: 10')

    def test_put_in_a_list(self):
        # test put_in_a_list function
        result = put_in_a_list(None)
        assert(result == [])

        result = put_in_a_list(10)
        assert (result == [10])

        t = (10, 20, 30)
        result = put_in_a_list(t)
        print(result)
        assert (result == [10, 20, 30])

        result = put_in_a_list((10, 20))
        assert (result == [10, 20])

        result = put_in_a_list('foo')
        assert (result == ['foo'])

        result = put_in_a_list(['foo', 'bar'])
        assert (result == ['foo', 'bar'])

        t = tuple('abc')
        result = put_in_a_list(t)
        print(result)
        assert (result == ['a', 'b', 'c'])
