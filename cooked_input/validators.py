"""
This file contains validator classes for cooked_input

For more validators: look at using validus:
    https://shopnilsazal.github.io/validus/readme.html

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import string
import re
import collections
import logging

from .error_callbacks import print_error, silent_error, DEFAULT_VALIDATOR_ERROR
from .input_utils import put_in_a_list


def in_any(value, validators, error_callback, validator_fmt_str):
    """
    return True if the value passes any of the validators - OR's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :param error_callback: the function to call when an error occurs in conversion or validation
    :param validator_fmt_str: format string fro convertor errors (defaults to DEFAULT_CONVERTOR_ERROR)

    :return: True if any of the validators pass, False if they all fail.
    """

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):  # list of validators (or other iterable)
        result = any(validator(value, error_callback, validator_fmt_str) for validator in validators)
    elif callable(validators):  # single validator function
        result = validators(value, error_callback, validator_fmt_str)
    else:   # single value
        result = value == validators

    return result


def in_all(value, validators, error_callback, validator_fmt_str):
    """
    return True if the value passes all of the validators - AND's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :param error_callback: function to call if an error occurs.
    :param validator_fmt_str: format string to pass to the error callback routine for formatting the error.

    :return: True if all of the validators pass, False if they all fail.
    """

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):
        result = all(validator(value, error_callback, validator_fmt_str) for validator in validators)
    elif callable(validators):
        result = validators(value, error_callback, validator_fmt_str)
    else:
        result = value == validators

    return result


def not_in(value, validators, error_callback, validator_fmt_str):
    """
    return True if the value does not pass any of the validators - NOT's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :param error_callback: function to call if an error occurs.
    :param validator_fmt_str: format string to pass to the error callback routine for formatting the error.

    :return: True if none of the validators pass, False if they any of them pass.
    """
    result = False

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):  # list of validators (or other iterable)
        for validator in validators:
            result = validator(value, silent_error, validator_fmt_str)
            if result:
                break
    elif callable(validators):  # single validator function
        result = validators(value, error_callback, validator_fmt_str)
    else:   # single value
        result = value == validators

    if not result:
        return True
    else:
        error_callback(validator_fmt_str, 'value', 'cannot match {}'.format(value))
        return False


def validate(value, validators, error_callback=print_error, validator_fmt_str=DEFAULT_VALIDATOR_ERROR):
    """
    Run validators on a value.

    :param value: the value to validate.
    :param validators: list of validators to run on the value.
    :param error_callback: function to call if an error occurs.
    :param validator_fmt_str: format string to pass to the error callback routine for formatting the error.
    :return: True if the input passed validation, else False
    """
    result = None

    if callable(validators):
        result = validators(value, error_callback, validator_fmt_str)
    else:
        for v in validators:
            result = v(value, error_callback, validator_fmt_str)
            if not result:
                break

    return result


####
#### Validators:
####
# class Validator(metaclass=ABCMeta): # introduced in Python 3
class Validator(object):
    # Abstract base class for validation classes
    def __init__(self, **kwargs):
        pass

    # @abstractmethod   # introduced in Python 3
    def __call__(self, value, error_callback, validator_fmt_str):
        pass


class ExactLengthValidator(Validator):
    """
    check a value is exactly a specified length

    :param length: the required length for the input
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, length=None, **kwargs):

        self._length = length
        super(ExactLengthValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        # TypeError thrown if value does not implement __len__
        val_len = len(value)
        condition1 = (self._length is None or val_len == self._length)

        if condition1:
            return True
        else:
            error_callback(validator_fmt_str, value, 'not length {}'.format(self._length))
            return False

    def __repr__(self):
        return 'ExactLengthValidator(value=%s)' % self._length


class InLengthValidator(Validator):
    """
    check a value is in between a length range (open interval).

    :param min_len: the minimum required length for the input. If None (the default), no minimum length is checked.
    :param max_len: the maximum required length for the input. If None (the default), no maximum length is checked.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, min_len=None, max_len=None, **kwargs):
        self._min_len = min_len
        self._max_len = max_len
        super(InLengthValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        # TypeError thrown if value does not implement __len__
        val_len = len(value)
        min_condition = (self._min_len is None or val_len >= self._min_len)
        max_condition = (self._max_len is None or val_len <= self._max_len)

        if min_condition and max_condition:
            return True
        elif not min_condition:
            error_callback(validator_fmt_str, value, 'too short (min_len={})'.format(self._min_len))
            return False
        else:
            error_callback(validator_fmt_str, value, 'too long (max_len={})'.format(self._max_len))
            return False

    def __repr__(self):
        return 'InLengthValidator(min_len=%s, max_len=%s)' % (self._min_len, self._max_len)


class ExactValueValidator(Validator):
    """
    check if a value is an exact value

    :param value: the value to match
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value, **kwargs):

        self._value = value
        super(ExactValueValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        condition1 = (self._value is None or value == self._value)

        if condition1:
            return True
        else:
            error_callback(validator_fmt_str, 'value', 'not equal to {}'.format(self._value))
            return False

    def __repr__(self):
        return 'ExactValueValidator(value=%s)' % self._value


class InRangeValidator(Validator):
    """
    check if a value is in between a minimum and maximum value (open interval). The value can be of any type as long
    as the __ge__ and __le__ comparison functions are defined.

    :param min_val: The minimum allowed value (i.e. value must be <= min_val). If None (the default), no minimum value is checked.
    :param max_val: The maximum allowed value (i.e. value must be >= min_val). If None (the default), no maximum value is checked.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, min_val=None, max_val=None, **kwargs):
        self._min_val = min_val
        self._max_val = max_val
        super(InRangeValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        min_condition = (self._min_val is None or value >= self._min_val)
        max_condition = (self._max_val is None or value <= self._max_val)

        if min_condition and max_condition:
            return True
        elif not min_condition:
            error_callback(validator_fmt_str, value, 'too low (min_val={})'.format(self._min_val))
            return False
        else:
            error_callback(validator_fmt_str, value, 'too high (max_val={})'.format(self._max_val))
            return False

    def __repr__(self):
        return 'InRangeValidator(min_val=%s, max_val=%s)' % (self._min_val, self._max_val)


class InChoicesValidator(Validator):
    """
    check if a value is in a list of choices. Note: if choices is mutable, it can be changed after the instance is created.

    :param choices: an iterable (tuple, list, or set) containing the allowed set of choice for the value.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, choices, **kwargs):
        # note: if choices is mutable, the choices can change after instantiation
        self._choices = put_in_a_list(choices)
        super(InChoicesValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = value in self._choices

        if result:
            return True
        else:
            error_callback(validator_fmt_str, 'value', 'must be one of: {}'.format(', '.join(self._choices)))
            return False

    def __repr__(self):
        return 'InChoicesValidator(choices={})'.format(self._choices)


class NotInValidator(Validator):
    """
    check if a value is not in a set of validators. Note: if choices is mutable, it can be changed after the instance is created.

    :param validators: an iterable list of validators that should not match the input value.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, validators, **kwargs):

        # note: if choices is mutable, the choices can change after instantiation
        self._validators = validators
        super(NotInValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = not_in(value, self._validators, error_callback, validator_fmt_str)

        # error callback handled within not_in call
        return result

    def __repr__(self):
        return 'NotInValidator(validators={})'.format(self._validators)


class InAnyValidator(Validator):
    """
    check if a value matches any of a set of validators (OR operation). Note: if choices is mutable, it can be changed after the instance is created.

    :param validators: an iterable list of validators. When the validators is called, return True once any of the validators matches.
    :param kwargs: kwargs: no kwargs are currently supported.

    """
    def __init__(self, validators, **kwargs):

        # note: if choices is mutable, the choices can change after instantiation
        self._validators = validators
        super(InAnyValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = in_any(value, self._validators, error_callback, validator_fmt_str)
        return result

    def __repr__(self):
        return 'InAnyValidator(validators={})'.format(self._validators)


class SimpleValidator(Validator):
    """
    check if a value matches any function that takes a single value as input and returns a Boolean. Used to wrap
    functions (e.g. validus validation functions see: [https://shopnilsazal.github.io/validus/].) Can also be used with func.partial [https://docs.python.org/3/library/functools.html]
    to wrap validation functions that take more complex parameters.

    :param validators an iterable list of validators. When the validators is called, return True once any of the validators matches.
    :param kwargs: kwargs: no kwargs are currently supported.

    optional kwargs:

        name: a string to use for the validator name in error messages

    """
    def __init__(self, validator_func, **kwargs):

        # note: if choices is mutable, the choices can change after instantiation
        self._validator = validator_func
        self._name = None

        for k, v in kwargs.items():
            if k == 'name':
                self._name = '%s' % v
            else:
                logging.warning('Warning: SimpleValidator received unknown option (%s)' % k)

        super_options_to_skip = {'name'}
        super_kwargs = {k: v for k, v in kwargs.items() if k not in super_options_to_skip}

        super(SimpleValidator, self).__init__(**super_kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = self._validator(value)

        if not result:
            error_callback(validator_fmt_str, value, 'is not a valid {}'.format(self._name))

        return result

    def __repr__(self):
        return 'InAnyValidator(validators={})'.format(self._validator)


class RegexValidator(Validator):
    """
    check if a value matches a regular expression.

    :param pattern: the regular expression to match.
    :param kwargs: kwargs: no kwargs are currently supported.
    
    options:
    
    regex_desc: a human readable string to use for the regex (used for error messages)
    """
    def __init__(self, pattern, **options):
        # note: if choices is mutable, the choices can change after instantiation
        self._regex = pattern
        self._regex_desc = pattern

        for k, v in options.items():
            if k == 'regex_desc':
                self._regex_desc = v
            else:
                logging.warning('Warning: get_input received unknown option (%s)' % k)

        super_options_to_skip = {'regex_desc'}
        super_kwargs = {k: v for k, v in options.items() if k not in super_options_to_skip}

        super(RegexValidator, self).__init__(**super_kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = re.search(self._regex, value)
        # return True if result else False
        if result:
            return True
        else:
            if self._regex == self._regex_desc:
                error_callback(validator_fmt_str, value, 'does not match pattern: {}'.format(self._regex_desc))
            else:
                error_callback(validator_fmt_str, value, 'is not a valid {}'.format(self._regex_desc))
            return False

    def __repr__(self):
        return 'RegexValidator(regex={})'.format(self._regex)


class PasswordValidator(Validator):
    """
    validate a password string.

    :param min_length: the minimum allowed password length. Defaults to 1
    :param max_length: the maximum password length. Defaults to 64
    :param min_lower: the minimum number of lower case letters. Defaults to None
    :param min_upper: the minimum number of upper case letters. Defaults to None
    :param min_digits: the minimum number of digits. Defaults to None
    :param min_puncts: the minimum number of punctuation characters. Defaults to None
    :param allowed: a string containing the allowed characters in the password. Defaults to upper and lower case ascii
        letters, plus digits, plus punctuation characters
    :param disallowed: a string containing characters not allowed in the password. Defaults to None
    :param kwargs: kwargs: no kwargs are currently supported.
    """
    def __init__(self, min_length=1, max_length=64, min_lower=0, min_upper=0, min_digits=0, min_puncts=0, allowed=None, disallowed=None, **kwargs):
        self.valid_chars = set(string.ascii_letters + string.digits + string.punctuation)
        # disallowed_chars = None

        self.min_length = min_length
        self.max_length = max_length
        self.min_lower = min_lower
        self.min_upper = min_upper
        self.min_digits = min_digits
        self.min_puncts = min_puncts
        self.disallowed = set(disallowed)

        if allowed is not None:
            self.valid_chars = set(allowed)
        elif disallowed is not None:
            # self.valid_chars -= set(disallowed)
            self.valid_chars -= self.disallowed

        super(PasswordValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        if len(set(value) - self.valid_chars):
            error_callback(validator_fmt_str, 'password', 'cannot contain any of the following characters: {}'.format(set(value) - self.valid_chars))
            return False

        if self.min_length and len(value) < self.min_length:
            error_callback(validator_fmt_str, 'password', 'too short (minimum length is {})'.format(self.min_length))
            return False

        if self.max_length and len(value) > self.max_length:
            error_callback(validator_fmt_str, 'password', 'too long (maximum length is {})'.format(self.max_length))
            return False

        if self.min_lower and len([c for c in value if c in string.ascii_lowercase]) < self.min_lower:
            error_callback(validator_fmt_str, 'password', 'too few lower case characters (minimum is {})'.format(self.min_lower))
            return False

        if self.min_upper and len([c for c in value if c in string.ascii_uppercase]) < self.min_upper:
            error_callback(validator_fmt_str, 'password', 'too few upper case characters (minimum is {})'.format(self.min_upper))
            return False

        if self.min_digits and len([c for c in value if c in string.digits]) < self.min_digits:
            error_callback(validator_fmt_str, 'password', 'too few digit characters (minimum is {})'.format(self.min_digits))
            return False

        if self.min_puncts and len([c for c in value if c in string.punctuation]) < self.min_puncts:
            error_callback(validator_fmt_str, 'password', 'too few punctuation characters (minimum is {} from)'.format(self.min_puncts,
                           set(string.punctuation) - self.disallowed))
            return False

        return True

    def __repr__(self):
        return 'PasswordValidator(allowed=%r, min_length=%r, max_length=%r, min_lowercase=%r, min_uppercase=%r, min_digits=%r, min_puncts=%r)' %\
               (self.valid_chars, self.min_length, self.max_length, self.min_lower, self.min_upper, self.min_digits, self.min_puncts)


class ListValidator(Validator):
    """
    Run a set of validators on a list.

    :param len_validator: a validator to run on the list length.
    :param elem_validators: a single or list of validators to apply to the elements of the list.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, len_validator=None, elem_validators=None, **kwargs):
        self._len_validator = len_validator
        self._elem_validators = elem_validators
        super(ListValidator, self).__init__(**kwargs)

    def __call__(self, value, error_callback, validator_fmt_str):
        if self._len_validator:
            result = self._len_validator(value, error_callback, validator_fmt_str)
            if not result:
                # error callback performed in len_validator
                return False

        if self._elem_validators:
            for item in value:
                result = validate(item, self._elem_validators, error_callback, validator_fmt_str)
                if not result:
                    # error callback performed in validate
                    return False

        return True

    def __repr__(self):
        return 'ListValidator()'.format()
