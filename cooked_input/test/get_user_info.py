"""
Example of using cooked_input to get user login information.

Note: uses validus for email validation. Requires "pip install validus"

Len Wanger, 2017
"""

from validus import isemail

from cooked_input import get_input
from cooked_input.cleaners import StripCleaner, LowerCleaner, CapitalizeCleaner
from cooked_input.convertors import ListConvertor
from cooked_input.validators import PasswordValidator, ListValidator, InChoicesValidator


if __name__ == '__main__':
    roles_list = ['admin', 'user', 'reviewer']

    strip_cleaner = StripCleaner()
    default_cleaners = [StripCleaner(), LowerCleaner()]
    name_cleaners = [StripCleaner(), CapitalizeCleaner()]
    strong_password_validator = PasswordValidator(disallowed='[]', min_length=5, max_length=15, min_lower=2, min_puncts=2)
    role_validtor = ListValidator(elem_validators=InChoicesValidator(roles_list))
    role_prompt = 'Roles ({}, separated by commas)'.format(sorted(roles_list))

    # Get information for the user:
    user_name = get_input(prompt='User name', cleaners=default_cleaners, blank_ok=False)
    password = get_input(prompt='Password', cleaners=None, validators=[strong_password_validator], blank_ok=False, hidden=True)
    first_name = get_input(prompt='First name', cleaners=name_cleaners, blank_ok=False)
    last_name = get_input(prompt='Last name', cleaners=name_cleaners, blank_ok=False)
    email = get_input(prompt='Email', cleaners=default_cleaners, validators=isemail, blank_ok=False)
    roles = get_input(prompt=role_prompt, cleaners=default_cleaners, convertor=ListConvertor(), validators=role_validtor, blank_ok=False)

    print('\nuser info: user_name: {}, password: {}, first_name: {}, last_name: {}, email: {}, roles: {}'.format(user_name, password, first_name, last_name, email, roles))
