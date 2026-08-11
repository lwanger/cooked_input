
"""
pytest tests for cooked_input -- test convertor functions


Len Wanger, 2017
"""

import decimal

import pytest

from cooked_input import get_input, get_boolean, get_list, get_date, get_yes_no, get_money
from cooked_input import Convertor, IntConvertor, BooleanConvertor, ListConvertor, DateConvertor, YesNoConvertor, DecimalConvertor
from cooked_input import StripCleaner


class TestConvertors(object):
    bool_convertor = BooleanConvertor()

    def test_the_base_convertor_cannot_be_instantiated(self):
        # Regression guard for #50, the same Python 2 __metaclass__ artifact Cleaner had:
        # the base was not actually abstract and its __call__ returned None.
        with pytest.raises(TypeError, match="abstract"):
            Convertor('')

    def test_a_subclass_implementing_call_is_concrete(self):
        class ShoutConvertor(Convertor):
            def __call__(self, value, error_callback, convertor_fmt_str):
                return value.upper()

        convertor = ShoutConvertor('a shout')
        assert convertor('quiet', None, None) == 'QUIET'
        assert convertor.value_error_str == 'a shout'
        # Unlike every concrete convertor in the library, the base defines no __repr__.
        assert repr(convertor).startswith('<cooked_input.tests.test_convertors.')

    def test_get_boolean_true(self, fake_input):
        input_str = u"""
            10
            
            true
            """

        fake_input(input_str)
        result = get_input(prompt='enter a boolean (True/False)', cleaners=StripCleaner(), convertor=self.bool_convertor)
        assert(result==True)

        assert repr(self.bool_convertor) == 'BooleanConvertor(true or false)'

    def test_get_boolean_false(self, fake_input):
        input_str = u"""
            10

            f
            """

        fake_input(input_str)
        result = get_input(prompt='enter a boolean (True/False)', cleaners=StripCleaner(), convertor=self.bool_convertor)
        assert (result == False)


    def test_get_bool(self, fake_input):
        input_str = u"""
            no
            """

        fake_input(input_str)
        result = get_boolean()
        assert (result == False)


    def test_get_list(self, fake_input):
        input_str = u"""
            foo, bar, blat
            """

        fake_input(input_str)
        result = get_list()
        assert (result == ['foo', 'bar', 'blat'])


    def test_get_input_list(self, fake_input):
        input_str = u"""
            foo, bar, blat
            """

        lc = ListConvertor()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=lc)
        assert (result == ['foo', 'bar', 'blat'])

        assert repr(lc) == 'ListConvertor(list of values)'


    def test_get_date(self, fake_input):
        input_str = u"""
            foo
            9/4/2017
            """

        fake_input(input_str)
        result = get_date()
        assert (str(result) == '2017-09-04 00:00:00')

    def test_get_input_date(self, fake_input):
        input_str = u"""
            9/4/2017
            """

        dc = DateConvertor()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=dc)
        assert (str(result) == '2017-09-04 00:00:00')

        assert repr(dc) == 'DateConvertor(a date)'


    def test_get_yes_no(self, fake_input):
        input_str = u"""
            foo
            Yes
            """

        fake_input(input_str)
        result = get_yes_no()
        assert (result == 'yes')

    def test_get_input_yes_no(self, fake_input):
        input_str = u"""
            foo
            No
            """

        ync = YesNoConvertor()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=ync)
        assert (result == 'no')
        assert repr(ync) == 'YesNoConvertor(yes or no)'

    def test_decimal(self, fake_input):
        input_str = u"""
            10.1
            10.10
            10.100
            """

        dc = DecimalConvertor(precision=2)
        good_result = decimal.Decimal('10.10')
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=dc)
        assert (result == good_result)
        assert repr(dc) == 'DecimalConvertor(precision=2, rounding=ROUND_HALF_UP, value_error_str=a decimal number)'

    def test_decimal2(self, fake_input):
        input_str = u"""
            10.1
            10.10
            10.100
            """

        dc = DecimalConvertor(precision=2, rounding="ROUND_UP")
        good_result = decimal.Decimal('10.10')
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=dc)
        assert (result == good_result)
        assert repr(dc) == 'DecimalConvertor(precision=2, rounding=ROUND_UP, value_error_str=a decimal number)'

    def test_get_money(self, fake_input):
        input_str = u"""
            $10.17
            10.17
            """

        good_result = decimal.Decimal('10.17')

        fake_input(input_str)
        result = get_money(symbol="$")
        assert (result == good_result)

    def test_get_money2(self, fake_input):
        input_str = u"""
            $1,000,012.17
            """

        good_result = decimal.Decimal('1000012.17')

        fake_input(input_str)
        result = get_money(symbol="$", separator=",")
        assert (result == good_result)
