"""
Test to test getting an integer values
"""

from io_get_input import get_input
from io_get_input.convertors import IntConvertor
from io_get_input.validators import InRangeValidator, ExactValueValidator, NotInValidator, InAnyValidator

if __name__ == '__main__':
    int_convertor = IntConvertor()
    pos_int_validator = InRangeValidator(min_val=1, max_val=None)
    zero_to_ten_validator = InRangeValidator(min_val=0, max_val=10)
    exactly_0_validator = ExactValueValidator(value=0)
    exactly_5_validator = ExactValueValidator(value=5)
    not_0_validator = NotInValidator(validators=[exactly_0_validator])
    in_0_or_5_validator = InAnyValidator(validators=[exactly_0_validator, exactly_5_validator])
    not_0_or_5_validator = NotInValidator(validators=[exactly_0_validator, exactly_5_validator])


    # get any integer - use a constructor for convertor, now the int_convertor variable
    print(get_input(convertor=IntConvertor(), prompt='Enter an integer'))

    # get any integer
    print(get_input(convertor=int_convertor, prompt='Enter an integer', default=5))

    # get a positive integer - use a single item for validators, not a list
    print(get_input(convertor=int_convertor, validators=pos_int_validator, prompt='Enter a positive integer'))

    # get an integer between 0 and ten
    print(get_input(convertor=int_convertor, validators=[zero_to_ten_validator], prompt='Enter an integer between 0 and 10'))

    # get zero - silly but makes more sense with the in any or not in validators
    print(get_input(convertor=int_convertor, validators=[exactly_0_validator], prompt='Enter 0'))

    # get zero or 5
    print(get_input(convertor=int_convertor, validators=[in_0_or_5_validator], prompt='Enter 0 or 5'))

    # get a non-zero integer
    print(get_input(convertor=int_convertor, validators=[not_0_validator], prompt='Enter a non-zero integer'))

    # get a non-zero integer between 0 and 10
    print(get_input(convertor=int_convertor, validators=[zero_to_ten_validator, not_0_validator], prompt='Enter a non-zero integer between 0 and 10'))

    # enter an integer besides zero or 5
    print(get_input(convertor=int_convertor, validators=[not_0_or_5_validator], prompt='Enter and integer besides 0 or 5'))
