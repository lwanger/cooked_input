"""
cooked input examples of getting inputs from tables

Len Wanger, 2017
"""


"""
Example of using cooked_input to get user login information. This example shows several features of 
cooked_input:

- Dealing with hidden inputs, retries, passwords, validating with validus, and writing custom validators.

First, it gets the login and password from the user, then it updates the user's profile information.

Warning: This is a simple example and does not represent what you would do in a secure environment. For
simplicity I have hard-coded a list of users with passwords hashed with the Python hash function. In
practice a call would be made to check the user name with the operating system. For instance, on Unix
systems the Python pwd module (part of the standard library) can be used:

    import pwd
    user_info = pwd.getpwnam(username)

The structure returned has the user ID and the encrypted passwd. To check the password, you encrypt the plain
text password and check it against the encrypted password. Something like this (on Unix systems):

    import pwd
    import crypt
    import getpass
    from hmac import compare_digest as compare_hash

    def compare_passwords(username, plaintext):
        stored_hash = pwd.getpwnam(username)[1]
        plaintext_hashed = crypt.crypt(plaintext)
        if compare_hash(plaintext_hashed, stored_hash):
            return True
        else:
            return False

Len Wanger, 2017
"""

import sys
from validus import isemail

from cooked_input import get_input
from cooked_input.cleaners import StripCleaner, LowerCleaner, CapitalizeCleaner
from cooked_input.convertors import ListConvertor
from cooked_input.validators import Validator, PasswordValidator, ListValidator, InChoicesValidator, ExactValueValidator
from cooked_input.validators import SimpleValidator


class CheckUserValidator(Validator):
    """
    This is a custom validator to check if a user is valid. For simplicity in this example I have
    hard-coded valid user names. In practice a call would be made to check the user name with the
    operating system. For instance, on Unix systems the Python pwd module (part of the standard library)
    can be used. See more details above.
    """
    def __init__(self, **kwargs):
        super(CheckUserValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        if value in user_list:
            return True
        else:
            valid_users = [ k for k in user_list.keys() ]
            error_callback(validator_fmt_str, value, 'not in list of users ({})'.format(valid_users))
            return False


class CheckPasswordValidator(Validator):
    """
    This is a custom validator to check whether the password matches the encrypted password for the user. For simplicity
    this in this example, I have hard-coded user information with passwords hashed with the Python hash function. In
    practice this is a very bad idea. See above for more details.

    """
    def __init__(self, username, **kwargs):
        self.username = username
        super(CheckPasswordValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        hashed_value = hash(value)
        is_match = user_list[self.username] == hashed_value

        if is_match:
            return True
        else:
            error_callback(validator_fmt_str, 'entered password', 'does not match current password'.format())
            return False


if __name__ == '__main__':
    # Fake list of users. passwords are encrypted with the Python hash function for simplicity. See warnings above!
    user_list = {
        'len': hash('12345'),
        'bob': hash('bob'),
        'jeff': hash('ffej'),
    }

    # Fake list of allowed roles
    roles_list = ['admin', 'user', 'reviewer']

    strip_cleaner = StripCleaner()
    default_cleaners = [StripCleaner(), LowerCleaner()]
    name_cleaners = [StripCleaner(), CapitalizeCleaner()]
    strong_password_validator = PasswordValidator(disallowed='[]', min_length=5, max_length=15, min_lower=2, min_puncts=2)
    email_validator = SimpleValidator(isemail, name='email')    # validator from validus function
    role_validtor = ListValidator(elem_validators=InChoicesValidator(roles_list))
    role_prompt = 'Roles ({}, separated by commas)'.format(sorted(roles_list))
    password_confirm_fmt_str = 'password does not match'

    # Simulate logging the user in:
    try:
        user_name = get_input(prompt='Username', cleaners=default_cleaners, validators=CheckUserValidator(), retries=3)
        password = get_input(prompt='Password', cleaners=None, validators=CheckPasswordValidator(user_name), hidden=True, retries=3)
    except RuntimeError:
        print('Maximum retries exceeded.... exiting')
        sys.exit(1)

    # Get updated profile information for the user:
    password = get_input(prompt='Enter new Password', cleaners=None, validators=strong_password_validator, hidden=True)

    try:
        password = get_input(prompt='Confirm new Password', cleaners=None, validators=ExactValueValidator(password),
                             hidden=True, retries=3, validator_error_fmt=password_confirm_fmt_str)
    except RuntimeError:
        print('Maximum retries exceeded.... exiting')
        sys.exit(1)

    first_name = get_input(prompt='First name', cleaners=name_cleaners)
    last_name = get_input(prompt='Last name', cleaners=name_cleaners)
    email = get_input(prompt='Email', cleaners=default_cleaners, validators=email_validator, blank_ok=False)
    roles = get_input(prompt=role_prompt, cleaners=default_cleaners, convertor=ListConvertor(), validators=role_validtor, blank_ok=False)

    print('\nUpdated user profile info: user_name: {}, password: {}, first_name: {}, last_name: {}, email: {}, roles: {}'.format(
        user_name, password, first_name, last_name, email, roles))
