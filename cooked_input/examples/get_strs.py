"""
cooked input examples of getting an string values

Len Wanger, 2017
"""

from cooked_input import get_input, get_string
from cooked_input.validators import ExactLengthValidator, InLengthValidator, InChoicesValidator, NotInValidator
from cooked_input.cleaners import StripCleaner, LowerCleaner, UpperCleaner
from cooked_input.cleaners import CapitalizeCleaner
from cooked_input.convertors import YesNoConvertor

if __name__ == '__main__':
    colors = ['red', 'green', 'blue']
    good_flavors = ['cherry', 'lime', 'lemon', 'orange']
    bad_flavors = 'licorice'

    length_3_validator = ExactLengthValidator(length=3)
    length_5_plus_validator = InLengthValidator(min_len=5)
    length_2_to_4_validator = InLengthValidator(min_len=2, max_len=4)
    choices_validator = InChoicesValidator(choices=colors)
    good_flavor_validator = InChoicesValidator(choices=good_flavors)
    bad_flavor_validator = InChoicesValidator(choices=bad_flavors)
    not_in_choices_validator = NotInValidator(validators=[bad_flavor_validator])

    strip_cleaner = StripCleaner()
    rstrip_cleaner = StripCleaner(lstrip=False, rstrip=True)
    lower_cleaner = LowerCleaner()
    upper_cleaner = UpperCleaner()
    capitalize_cleaner = CapitalizeCleaner(all_words=False)
    capitalize_all_cleaner = CapitalizeCleaner(all_words=True)
    strip_and_lower_cleaners = [strip_cleaner, lower_cleaner]


    # simplest way
    print(get_string())

    # get any string
    print(get_input(prompt='Enter any string'))
    print(get_input(prompt='Enter any string', blank_ok=True))
    print(get_input(prompt='Enter any string (will be stripped of leading and trailing spaces and converted to lower)',
                    cleaners=strip_and_lower_cleaners))
    print(get_input(prompt='Enter any string (will be stripped of trailing spaces and converted to upper)',
                    cleaners=[rstrip_cleaner, upper_cleaner]))

    # capitalization cleaning (CapitalizeCleaner)
    print(get_input(prompt='Enter your name (first word will be capitalized)', cleaners=capitalize_cleaner))
    print(get_input(prompt='Enter your name (all words will be capitalized)', cleaners=capitalize_all_cleaner))

    # picking from choices (InchoicesValidator)
    prompt_str = "What is your favorite flavor jelly bean (pick any flavor, don't say licorice!)?"
    print(get_input(prompt=prompt_str, validators=not_in_choices_validator, default='cherry'))

    prompt_str = "Which of these is your favorite flavor jelly bean (choose from: %s, but not licorice!)?" % ', '.join(good_flavors)
    validators = [good_flavor_validator, not_in_choices_validator]
    print(get_input(prompt=prompt_str, cleaners=strip_and_lower_cleaners, validators=validators, default='cherry'))

    # get different length strings
    print(get_input(prompt='Enter a three letter string', validators=[length_3_validator]))
    print(get_input(prompt='Enter a string at least 5 letters long', validators=[length_5_plus_validator]))
    print(get_input(prompt='Enter a 2 to 4 letter string', validators=[length_2_to_4_validator]))

    # Use YesNoConvertor
    print(get_input(prompt="Yes or no?", cleaners=strip_cleaner, convertor=YesNoConvertor(), default='Y'))
