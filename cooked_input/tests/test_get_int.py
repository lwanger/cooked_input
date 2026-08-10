
"""
pytest tests for cooked_input

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


from cooked_input import get_input, get_int, silent_error, log_error
from cooked_input import IntConvertor, RangeValidator, EqualToValidator
from cooked_input import NoneOfValidator, AnyOfValidator


def my_print_error(fmt_str, value, error_content):
    """A user-supplied error callback, recording instead of printing.

    Keeping the formatted messages lets a test assert which values were rejected
    and with what wording, which printing them never could.
    """
    my_print_error.messages.append('<<< ' + fmt_str.format(value=value, error_content=error_content) + ' >>>')


my_print_error.messages = []


class TestGetInt(object):
    int_convertor = IntConvertor()
    pos_int_validator = RangeValidator(min_val=1, max_val=None)
    zero_to_ten_validator = RangeValidator(min_val=0, max_val=10)
    exactly_0_validator = EqualToValidator(value=0)
    exactly_5_validator = EqualToValidator(value=5)
    not_0_validator = NoneOfValidator(validators=[exactly_0_validator])
    not_5_validator = NoneOfValidator(validators=[exactly_5_validator])
    in_0_or_5_validator = AnyOfValidator(validators=[exactly_0_validator, exactly_5_validator])
    not_0_or_5_validator = NoneOfValidator(validators=[exactly_0_validator, exactly_5_validator])
    convertor_fmt = '# {value} cannot be converted to {error_content} #'
    validator_fmt = '@ {value} {error_content} @'


    def test_get_input_int(self, fake_input):
        input_str = u"""
            10
            5
            -1
            1
    
            """

        irv = RangeValidator(min_val=1, max_val=10)
        fake_input(input_str)
        result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
        assert(result==10)

        result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
        assert(result==5)

        result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
        assert(result==1)

        assert repr(self.int_convertor) == 'IntConvertor(base=10, value_error_str=an integer number)'


    def test_ignore_bad_conversion(self, fake_input):
        input_str = u"""
            foo
            101
            """

        fake_input(input_str)
        result = get_input(prompt='Enter an integer', convertor=IntConvertor())
        assert(result==101)


    def test_use_default_value(self, fake_input):
        input_str = u"""

            """

        fake_input(input_str)
        result = get_input(prompt='Enter an integer', convertor=IntConvertor(), default=5)
        assert (result == 5)


    def test_get_pos_int(self, fake_input):
        input_str = u"""
            -1
            0
            10
            """

        fake_input(input_str)
        result = get_input(convertor=IntConvertor(), validators=self.pos_int_validator, prompt='Enter a positive integer')
        assert (result == 10)


    def test_get_0_to_10(self, fake_input):
        input_str = u"""
            -1
            11
            0
            """

        fake_input(input_str)
        result = get_input(convertor=self.int_convertor, validators=[self.zero_to_ten_validator],
                    prompt='Enter an integer between 0 and 10')
        assert (result == 0)


    def test_exactly_val(self, fake_input):
        # get zero - silly but makes more sense with the in any or not in validators
        input_str = u"""
            1
            0
            """

        fake_input(input_str)
        result = get_input(convertor=self.int_convertor, validators=[self.exactly_0_validator], prompt='Enter 0')
        assert (result == 0)


    def test_in_any_val(self, fake_input):
        # get zero or 5
        input_str = u"""
            foo
            1
            5
            """

        fake_input(input_str)
        result = get_input(convertor=self.int_convertor, validators=[self.in_0_or_5_validator], prompt='Enter 0 or 5')
        assert (result == 5)


    def test_not_in(self, fake_input):
        # get a non-zero integer
        input_str = u"""
            0
            -101
            """

        fake_input(input_str)
        result = get_input(convertor=self.int_convertor, validators=[self.not_0_validator], prompt='Enter a non-zero integer')
        assert (result == -101)


    def test_in_range_and_not_in(self, fake_input):
        # get a non-zero integer between 0 and 10
        input_str = u"""
            0
            -1
            11
            5
            """

        fake_input(input_str)
        result = get_input(convertor=self.int_convertor, validators=[self.zero_to_ten_validator, self.not_0_validator],
                    prompt='Enter a non-zero integer between 0 and 10')
        assert (result == 5)


    def test_mult_not_in(self, fake_input):
        # enter an integer besides zero or 5
        input_str = u"""
            0
            5
            -101
            """

        fake_input(input_str)
        result = get_input(convertor=self.int_convertor, validators=[self.not_0_or_5_validator],
                    prompt='Enter and integer besides 0 or 5')
        assert (result == -101)


    def test_error_callback(self, fake_input):
        # test error callbacks and format strings
        input_str = u"""
            foo
            -1
            12
            5
            7
            """

        my_print_error.messages.clear()
        fake_input(input_str)
        result = get_input(convertor=IntConvertor(), validators=[self.zero_to_ten_validator, self.not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5 (my_print_error)',
                    error_callback=my_print_error,
                    convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
        assert (result == 7)

        # Four bad values, four calls -- and the callback receives the caller's own
        # format strings, not the library defaults.
        assert len(my_print_error.messages) == 4
        assert all(m.startswith('<<< ') and m.endswith(' >>>') for m in my_print_error.messages)
        assert 'foo' in my_print_error.messages[0]


    def test_silent_error(self, fake_input):
        input_str = u"""
            foo
            -1
            12
            5
            5
            4
            """

        fake_input(input_str)
        result = get_input(convertor=IntConvertor(), validators=[self.zero_to_ten_validator, self.not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5 (errors not printed)',
                    error_callback=silent_error,
                    convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
        assert (result == 4)


    def test_log_error(self, fake_input):
        input_str = u"""
            foo
            -1
            12
            5
            5
            4
            """

        fake_input(input_str)
        result = get_input(convertor=IntConvertor(), validators=[self.zero_to_ten_validator, self.not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5 (errors not printed)',
                    error_callback=log_error)
        assert (result == 4)


    def test_get_int(self, fake_input):
        input_str = u"""
            foo
            3.14
            101
            5
            """

        fake_input(input_str)
        result = get_int()
        assert (result == 101)

        fake_input(input_str)
        result = get_int(prompt='Enter an integer')
        assert (result == 101)

        fake_input(input_str)
        result = get_int(validators=[self.zero_to_ten_validator],
                    error_callback=my_print_error,
                    convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
        assert (result == 5)

        fake_input(input_str)
        result = get_int(validators=[self.zero_to_ten_validator],
                    prompt='Enter a integer between 0 and 10',
                    error_callback=my_print_error,
                    convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
        assert (result == 5)

    def test_get_int_part2(self, fake_input):
        input_str = u"""
            foo
            3.14
            101
            5
            """

        fake_input(input_str)
        result = get_int(validators=self.not_0_validator, prompt='Enter an integer that is not 0')
        assert (result == 101)

        input_str = u"""
            -11
            11
            5
            """
        fake_input(input_str)
        result = get_int(validators=None, minimum=-10, maximum=10, prompt='Enter an integer between -10 and 10')
        assert (result == 5)

        fake_input(input_str)
        result = get_int(validators=None, minimum=1, prompt='Enter an integer greater than 0')
        assert (result == 11)

        fake_input(input_str)
        result = get_int(validators=None, maximum=10, prompt='Enter an integer less than than 11')
        assert (result == -11)

        input_str = u"""
            -11
            11
            0
            5
            6
            """
        fake_input(input_str)
        result = get_int(validators=None, minimum=1, maximum=10, prompt='Enter an integer between 1 and 10')
        assert (result == 5)

        fake_input(input_str)
        result = get_int(validators=self.not_0_validator, minimum=-10, maximum=10,
                  prompt='Enter an integer between -10 and 10, but not 0')
        assert (result == 5)

        fake_input(input_str)
        result = get_int(validators=[self.not_0_validator, self.not_5_validator], minimum=-10, maximum=10,
                  prompt='Enter an integer between -10 and 10, but not 0 or 5')
        assert (result == 6)
