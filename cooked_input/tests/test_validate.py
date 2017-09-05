
"""
pytest tests for cooked_input: test the validate method

Len Wanger, 2017
"""

from io import StringIO

from cooked_input import validate, RangeValidator, NoneOfValidator
from cooked_input import get_input, StripCleaner, IntConvertor, ListConvertor, AnyOfValidator, NoneOfValidator, LengthValidator
from cooked_input import EqualToValidator, ListValidator

from .utils import redirect_stdin


class TestValidate(object):

    def test_validate(self):
        result = validate(3, validators=RangeValidator(min_val=1, max_val=10))
        assert (result == 1)

        validators = [RangeValidator(min_val=1, max_val=10), NoneOfValidator(5)]

        for v in [(-1, False), (1, True), (5, False), (6, True), (11, False)]:
            result = validate(v[0], validators)
            assert(result==v[1])


    def test_any_of(self):
        input_str = u"""
            -1
            6
            16
            2
            """

        av = AnyOfValidator(validators=[RangeValidator(0,5), RangeValidator(10,15)])
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
            print(result)
            assert (result == 2)

        print(av)   # for code coverage

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=None)
            print(result)
            assert (result == -1)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=RangeValidator(5,10))
            print(result)
            assert (result == 6)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=16)
            print(result)
            assert (result == 16)


        av = AnyOfValidator(validators=16)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
            print(result)
            assert (result == 16)


    def test_none_of(self):
        input_str = u"""
            -1
            6
            16
            2
            """

        nov = NoneOfValidator(validators=[RangeValidator(0,5), RangeValidator(10,15)])
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=nov)
            print(result)
            assert (result == -1)

        print(nov)   # for code coverage


    def test_length(self):
        input_str = u"""
            1
            foo
            foobar
            foob
            fb
            """

        lv = LengthValidator()
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == '1')

        print(lv)   # for code coverage

        lv = LengthValidator(min_len=2)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == 'foo')

        lv = LengthValidator(max_len=2)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == '1')

        lv = LengthValidator(min_len=4, max_len=5)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == 'foob')


    def test_equal(self):
        input_str = u"""
            1
            3
            """

        ev = EqualToValidator(3)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=ev)
            print(result)
            assert (result == 3)

        print(ev)   # for code coverage


    def test_list(self):
        input_str = u"""
            1
            3,4,5,6,7
            2,3,4
            """

        lc = ListConvertor(elem_convertor=IntConvertor())
        lv = ListValidator(len_validator=LengthValidator(min_len=2, max_len=7))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc, validators=lv)
            print(result)
            assert (result == [3,4,5,6,7])

        print(lv)   # for code coverage

        lv = ListValidator(len_validator=LengthValidator(min_len=2), elem_validators=RangeValidator(max_val=6))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc, validators=lv)
            print(result)
            assert (result == [2,3,4])