
"""
pytest tests for cooked_input: test the validate method

Len Wanger, 2017
"""

import pytest


from cooked_input import validate, Validator, RangeValidator, NoneOfValidator
from cooked_input import GetInput, get_input, print_error, StripCleaner, IntConvertor, ListConvertor, AnyOfValidator
from cooked_input import NoneOfValidator, LengthValidator
from cooked_input import EqualToValidator, ListValidator, PasswordValidator, ChoiceValidator, SimpleValidator, RegexValidator


class TestValidate(object):

    def test_validate(self):
        result = validate(3, validators=RangeValidator(min_val=1, max_val=10))
        assert (result == 1)

        validators = [RangeValidator(min_val=1, max_val=10), NoneOfValidator(5)]

        for v in [(-1, False), (1, True), (5, False), (6, True), (11, False)]:
            result = validate(v[0], validators)
            assert(result==v[1])

    def test_bad_type(self):
        # For specific test coverage cases to catch no __ge__ specified on type
        class A(object):
            a=1

        # RangeValidator catches the TypeError from comparing an object that
        # defines neither __ge__ nor __le__, and reports failure rather than
        # letting it escape. Both bounds exercise a different comparison.
        assert validate(A(), RangeValidator(min_val=1, max_val=None)) is False
        assert validate(A(), RangeValidator(min_val=None, max_val=10)) is False

    def test_the_base_validator_cannot_be_instantiated(self):
        # Regression guard for #50: the Python 2 __metaclass__ spelling left this base
        # instantiable, and its __call__ returned None -- which reads as a validation
        # failure, so a subclass that forgot __call__ quietly rejected everything.
        with pytest.raises(TypeError, match="abstract"):
            Validator()

    def test_a_subclass_implementing_call_is_concrete(self):
        class EvenValidator(Validator):
            def __call__(self, value, error_callback, validator_fmt_str):
                return value % 2 == 0

        assert validate(4, EvenValidator()) is True
        assert validate(5, EvenValidator()) is False


    def test_any_of(self, fake_input):
        input_str = u"""
            -1
            6
            16
            2
            """

        av = AnyOfValidator(validators=[RangeValidator(0,5), RangeValidator(10,15)])
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
        assert (result == 2)

        assert repr(av) == 'AnyOfValidator(validators=[RangeValidator(min_val=0, max_val=5), RangeValidator(min_val=10, max_val=15)])'

        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=None)
        assert (result == -1)

        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=RangeValidator(5,10))
        assert (result == 6)

        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=16)
        assert (result == 16)

        av = AnyOfValidator(validators=EqualToValidator(16))
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
        assert (result == 16)

        av = AnyOfValidator(validators=16)
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
        assert (result == 16)

        av = AnyOfValidator(validators=None)
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
        assert (result == -1)


    def test_none_of(self, fake_input):
        input_str = u"""
            -1
            6
            16
            2
            """

        nov = NoneOfValidator(validators=[RangeValidator(0,5), RangeValidator(10,15)])
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=nov)
        assert (result == -1)

        assert repr(nov) == 'NoneOfValidator(validators=[RangeValidator(min_val=0, max_val=5), RangeValidator(min_val=10, max_val=15)])'

        nov = NoneOfValidator(validators=RangeValidator(-2,5))
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=nov)
        assert (result == 6)


    def test_length(self, fake_input):
        input_str = u"""
            1
            foo
            foobar
            foob
            fb
            """

        lv = LengthValidator()
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), validators=lv)
        assert (result == '1')

        assert repr(lv) == 'LengthValidator(min_len=None, max_len=None)'

        lv = LengthValidator(min_len=2)
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), validators=lv)
        assert (result == 'foo')

        lv = LengthValidator(max_len=2)
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), validators=lv)
        assert (result == '1')

        lv = LengthValidator(min_len=4, max_len=5)
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), validators=lv)
        assert (result == 'foob')


    def test_equal(self, fake_input):
        input_str = u"""
            1
            3
            """

        ev = EqualToValidator(3)
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=ev)
        assert (result == 3)

        assert repr(ev) == 'EqualToValidator(value=3)'


    def test_list(self, fake_input):
        input_str = u"""
            1
            3,4,5,6,7
            2,3,4
            """

        lc = ListConvertor(elem_get_input=GetInput(convertor=IntConvertor()))
        lv = ListValidator(len_validators=RangeValidator(min_val=2, max_val=7))
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=lc, validators=lv)
        assert (result == [3,4,5,6,7])

        assert repr(lv) == 'ListValidator()'

        lv = ListValidator(len_validators=RangeValidator(min_val=2), elem_validators=RangeValidator(max_val=6))
        fake_input(input_str)
        result = get_input(cleaners=StripCleaner(), convertor=lc, validators=lv)
        assert (result == [2,3,4])

    def test_password(self, fake_input):
        # Migrated off redirect_stdin ahead of the rest of the suite: the two
        # hidden=True cases below route through getpass, which ignores a reassigned
        # sys.stdin whenever it can open /dev/tty. Under redirect_stdin they passed
        # only because CI runners have no tty and win_getpass falls back when
        # sys.stdin is not sys.__stdin__ -- on a Linux or macOS box run from a real
        # terminal they read the actual keyboard and hung.
        input_str = "\nfoo\nfooFFFF\nffffffffoooooobbbb\nFOOBAR!\nfoobar!\nFooBar!\nFooBar1!\nFooBar1!!\nfbr^"
        any_password_val = PasswordValidator()

        fake_input(input_str)
        assert get_input(validators=any_password_val) == 'foo'

        assert 'PasswordValidator' in repr(any_password_val)

        feeder = fake_input(input_str)
        result = get_input(validators=[any_password_val], prompt='type in any password', required=False, hidden=True)
        assert result is None
        # Proves the hidden path really was exercised through the fixture rather
        # than quietly falling back to the visible one.
        assert feeder.hidden_prompts

        stronger_password_val = PasswordValidator(allowed='fobarFOB1!^', disallowed='[]', min_len=5, max_len=15, min_lower=4, min_upper=2, min_digits=1, min_puncts=2)

        feeder = fake_input(input_str)
        result = get_input(validators=[stronger_password_val],
                           prompt='type in a password (length=5-15, with at least 2 lower, 2 upper, 1 digit, and 2 puncts)', hidden=True)
        assert result == 'FooBar1!!'
        assert feeder.hidden_prompts

        disallowed_chars = 'aeiou!*&%2468'
        disallowed_chars_password_val = PasswordValidator(disallowed=disallowed_chars)

        fake_input(input_str)
        result = get_input(validators=[disallowed_chars_password_val], prompt='type in a password (type in a password(no vowels, even digits or !, *, \\ %)')
        assert result == 'fbr^'

    def test_password_validator_rejects_a_non_string(self, capsys):
        # A non-string cannot be a password; the validator says so on stderr and
        # returns False rather than blowing up on len() or str.islower().
        pv = PasswordValidator()
        assert pv(10, print_error, "{value}") is False
        assert '10' in capsys.readouterr().err

    def test_choices(self, fake_input):
        input_str = "\nfoo\nffffffffoooooobbbb\nFOOBAR!\nfoobar!\nFooBar!\nfoobar\nFooBar1!\nFooBar1!!\nfbr^"
        cv = ChoiceValidator(choices=['foobar', 'bar', 'blat'])

        fake_input(input_str)
        result = get_input(validators=cv)
        assert (result == 'foobar')

        assert repr(cv) == "ChoiceValidator(choices=['foobar', 'bar', 'blat'])"

    def test_simple(self, fake_input):
        def simple_func(value):
            return True if value == 'foobar' else False

        input_str = "\nfoo\nffffffffoooooobbbb\nFOOBAR!\nfoobar!\nFooBar!\nfoobar\nFooBar1!\nFooBar1!!\nfbr^"
        sv = SimpleValidator(validator_func=simple_func, name='simple validator')

        fake_input(input_str)
        result = get_input(validators=sv)
        assert (result == 'foobar')

        assert repr(sv).startswith('SimpleValidator(validators=<function TestValidate.test_simple.<locals>.simple_func')

        sv = SimpleValidator(validator_func=simple_func, name='bad option')


    def test_regex(self, fake_input):
        input_str = "\n1234\n2345678901"
        rev = RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='a 10 digit phone number')

        fake_input(input_str)
        result = get_input(validators=rev)
        assert (result == '2345678901')

        assert repr(rev) == 'RegexValidator(regex=^[2-9]\\d{9}$)'

        rev = RegexValidator(pattern=r'^[2-9]\d{9}$')

        fake_input(input_str)
        result = get_input(validators=rev)
        assert (result == '2345678901')

        with pytest.raises(EOFError):
            fake_input(input_str)
            result = get_input(convertor=IntConvertor(), validators=rev)

        rev = RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='bad option')

