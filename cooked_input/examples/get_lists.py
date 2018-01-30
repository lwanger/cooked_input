"""
cooked input examples of getting an list values

Len Wanger, 2017
"""

from cooked_input import get_input, get_list, GetInputInterrupt
from cooked_input.validators import LengthValidator, ChoiceValidator, ListValidator
from cooked_input.cleaners import StripCleaner, CapitalizationCleaner
from cooked_input.convertors import ListConvertor, IntConvertor, YesNoConvertor

if __name__ == '__main__':
    colors = ['red', 'green', 'blue']
    length_3_validator = LengthValidator(min_len=3, max_len=3)
    length_5_plus_validator = LengthValidator(min_len=5)
    length_2_to_4_validator = LengthValidator(min_len=2, max_len=4)
    color_validator = ChoiceValidator(choices=colors)

    strip_cleaner = StripCleaner()
    lower_cleaner = CapitalizationCleaner()
    upper_cleaner = CapitalizationCleaner(style='upper')

    # simplest way
    print(get_list())

    # get any list
    print(get_input(prompt='Enter a list (separated by commas)', convertor=ListConvertor()))
    print(get_input(prompt='Enter a list (separated by commas, blank not OK)', convertor=ListConvertor(),  required=True))
    print(get_input(prompt='Enter a list (separated by commas, blank OK)', convertor=ListConvertor(), required=False))
    print(get_input(prompt='Enter a list (separated by commas, stripped)', convertor=ListConvertor(), cleaners=strip_cleaner))

    # specified delimiter
    print(get_input(prompt='Enter a list (separated by |)', convertor=ListConvertor(delimiter='|')))
    print(get_input(prompt='Enter a list (separated by tabs)', convertor=ListConvertor(delimiter='\t')))

    # length of list
    print(get_input(prompt='Enter a list (len=3)', convertor=ListConvertor(), validators=ListValidator(len_validator=length_3_validator)))
    print(get_input(prompt='Enter a list (len=5+)', convertor=ListConvertor(), validators=ListValidator(len_validator=length_5_plus_validator)))
    print(get_input(prompt='Enter a list (len=2-4)', convertor=ListConvertor(), validators=ListValidator(len_validator=length_2_to_4_validator)))

    # items in list of type int, float, or string (homogenous)
    print(get_input(prompt='Enter a list (ints)', convertor=ListConvertor(elem_convertor=IntConvertor()), validators=ListValidator()))
    print(get_input(prompt='Enter a list (of yes/no)', convertor=ListConvertor(elem_convertor=YesNoConvertor()), validators=ListValidator()))

    # items in list from list of choices
    print(get_input(prompt='Enter a list (colors=red|green|blue)', convertor=ListConvertor(), validators=ListValidator(elem_validators=[color_validator])))

    # len and elem validators:
    print(get_input(prompt='Enter a list (ints, len=3)', convertor=ListConvertor(elem_convertor=IntConvertor()), validators=ListValidator(len_validator=length_3_validator)))
