
"""
pytest tests for cooked_input -- test convertor functions


Len Wanger, 2017
"""

import decimal


from cooked_input import get_input, get_boolean, get_list, get_date, get_yes_no, get_money
from cooked_input import Convertor, IntConvertor, BooleanConvertor, ListConvertor, DateConvertor, YesNoConvertor, DecimalConvertor
from cooked_input import StripCleaner


class TestConvertors(object):
    bool_convertor = BooleanConvertor()

    def test_base_class(self):
        c = Convertor('')
        c('foo', None, None) # for coverage testing only!

    def test_get_boolean_true(self, fake_input):
        input_str = u"""
            10
            
            true
            """

        fake_input(input_str)
        result = get_input(prompt='enter a boolean (True/False)', cleaners=StripCleaner(), convertor=self.bool_convertor)
        print(result)
        assert(result==True)

        print(self.bool_convertor)   # for code coverage

    def test_get_boolean_false(self, fake_input):
        input_str = u"""
            10

            f
            """

        fake_input(input_str)
        result = get_input(prompt='enter a boolean (True/False)', cleaners=StripCleaner(), convertor=self.bool_convertor)
        print(result)
        assert (result == False)


    def test_get_bool(self, fake_input):
        input_str = u"""
            no
            """

        fake_input(input_str)
        result = get_boolean()
        print(result)
        assert (result == False)


    def test_get_list(self, fake_input):
        input_str = u"""
            foo, bar, blat
            """

        fake_input(input_str)
        result = get_list()
        print(result)
        assert (result == ['foo', 'bar', 'blat'])


    def test_get_input_list(self, fake_input):
        input_str = u"""
            foo, bar, blat
            """

        lc = ListConvertor()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=lc)
        print(result)
        assert (result == ['foo', 'bar', 'blat'])

        print(lc)   # for code coverage


    def test_get_date(self, fake_input):
        input_str = u"""
            foo
            9/4/2017
            """

        fake_input(input_str)
        result = get_date()
        print(result)
        assert (str(result) == '2017-09-04 00:00:00')

    def test_get_input_date(self, fake_input):
        input_str = u"""
            9/4/2017
            """

        dc = DateConvertor()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=dc)
        print(result)
        assert (str(result) == '2017-09-04 00:00:00')

        print(dc)   # for code coverage


    def test_get_yes_no(self, fake_input):
        input_str = u"""
            foo
            Yes
            """

        fake_input(input_str)
        result = get_yes_no()
        print(result)
        assert (result == 'yes')

    def test_get_input_yes_no(self, fake_input):
        input_str = u"""
            foo
            No
            """

        ync = YesNoConvertor()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=ync)
        print(result)
        assert (result == 'no')
        print(ync)

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
        print(result)
        assert (result == good_result)
        print(dc)

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
        print(result)
        assert (result == good_result)
        print(dc)

    def test_get_money(self, fake_input):
        input_str = u"""
            $10.17
            10.17
            """

        good_result = decimal.Decimal('10.17')

        fake_input(input_str)
        result = get_money(symbol="$")
        print(result)
        assert (result == good_result)

    def test_get_money2(self, fake_input):
        input_str = u"""
            $1,000,012.17
            """

        good_result = decimal.Decimal('1000012.17')

        fake_input(input_str)
        result = get_money(symbol="$", separator=",")
        print(result)
        assert (result == good_result)