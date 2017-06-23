"""
Test to test getting a string values


- show cleaners: strip, upper, lower
"""

from io_get_input import get_input
from io_get_input.validators import ExactLengthValidator, InLengthValidator, InChoicesValidator, NotInValidator
from io_get_input.cleaners import StripCleaner, LowerCleaner, UpperCleaner

if __name__ == '__main__':
    colors = ['red', 'green', 'blue']
    flavors = 'licorice'

    length_3_validator = ExactLengthValidator(length=3)
    length_5_plus_validator = InLengthValidator(min_len=5)
    length_2_to_4_validator = InLengthValidator(min_len=2, max_len=4)
    choices_validator = InChoicesValidator(choices=colors)
    flavor_validator = InChoicesValidator(choices=flavors)
    not_in_choices_validator = NotInValidator(validators=[flavor_validator])

    strip_cleaner = StripCleaner()
    lower_cleaner = LowerCleaner()
    upper_cleaner = UpperCleaner()

    # get any string
    print(get_input(prompt='Enter any string'))
    print(get_input(prompt='Enter any string', blank_ok=True))
    print(get_input(prompt='Enter any string (will be stripped of leading and trailing spaces and converted to lower)',
            cleaners=[strip_cleaner, lower_cleaner]))
    print(get_input(prompt='Enter any string (will be stripped of trailing spaces and converted to upper)',
            cleaners=[strip_cleaner, upper_cleaner]))

    print(get_input(prompt="What is your favorite flavor jelly bean (don't say licorice!)?", validators=not_in_choices_validator, default='cherry'))

    # get different length strings
    print(get_input(prompt='Enter a three letter string', validators=[length_3_validator]))
    print(get_input(prompt='Enter a string at least 5 letters long', validators=[length_5_plus_validator]))
    print(get_input(prompt='Enter a 2 to 4 letter string', validators=[length_2_to_4_validator]))

    # Use InChoicesValidator
    prompt_str = 'What is your favorite color (%s)' % ', '.join(colors)
    print(get_input(prompt=prompt_str, default='green'))