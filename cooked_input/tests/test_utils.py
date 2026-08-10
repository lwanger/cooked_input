
"""
pytest tests for cooked_input: test the utility functions

Len Wanger, 2017
"""

import pytest

from cooked_input.input_utils import compose, put_in_a_list
from cooked_input.input_utils import swap_element, renumerate, cap_last_word

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
        assert (result == [10, 20, 30])

        result = put_in_a_list((10, 20))
        assert (result == [10, 20])

        result = put_in_a_list('foo')
        assert (result == ['foo'])

        result = put_in_a_list(['foo', 'bar'])
        assert (result == ['foo', 'bar'])

        t = tuple('abc')
        result = put_in_a_list(t)
        assert (result == ['a', 'b', 'c'])

    def test_renumerate(self):
        values = reversed(list(enumerate('bar')))
        for i,v in renumerate('bar'):
            assert(next(values)==(i,v))

        values = reversed(list(enumerate([10, 20, 30])))
        for i, v in renumerate([10, 20, 30]):
            assert (next(values) == (i, v))

    def test_swap_element(self):
        # The old table had no expected column -- its third element is the
        # replacement character, not the result -- so the loop below computed
        # results and threw them all away. Negative indices count from the end.
        cases = [
            ('foo', 0, 'F', 'Foo'),
            ('foo', 1, 'O', 'fOo'),
            ('foo', 2, 'O', 'foO'),
            ('foo', -3, 'F', 'Foo'),
            ('foo', -2, 'O', 'fOo'),
            ('foo', -1, 'O', 'foO'),
            ('f', 0, 'F', 'F'),
            ('f', -1, 'F', 'F'),
        ]
        for sequence, index, replacement, expected in cases:
            assert swap_element(sequence, index, replacement) == expected

        values = [
            ('foo', 4, 'O'),  # IndexError
            ('foo', -4, 'O'),  # IndexError
        ]
        for v in values:
            with pytest.raises(IndexError):
                swap_element(v[0], v[1], v[2])

        values = [
            ('', 0, 'F'),  # ValueError
        ]
        for v in values:
            with pytest.raises(ValueError):
                swap_element(v[0], v[1], v[2])

    def test_cap_last_word(self):
        values = [
            ('foo', 'Foo'),
            ('foo bar', 'foo Bar'),
            ('   \t ', '   \t '),
        ]

        for value in values:
            result = cap_last_word(value[0])
            assert(result == value[1])
