"""
This file contains validator classes for cooked_input

For more validators: look at using validus:
    https://shopnilsazal.github.io/validus/readme.html

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

from __future__ import print_function

import os
import sys
import string
import re
import collections
import logging
from abc import ABCMeta, abstractmethod


from .error_callbacks import print_error, silent_error, DEFAULT_VALIDATOR_ERROR
from .input_utils import put_in_a_list, isstring


def in_any(value, validators, error_callback, validator_fmt_str):
    """
    return True if the value passes any of the validators - OR's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :param error_callback: the function to call when an error occurs in conversion or validation
    :param validator_fmt_str: format string fro convertor errors (defaults to DEFAULT_CONVERTOR_ERROR)

    :return: **True** if any of the validators pass, **False** if they all fail.
    """

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):  # list of validators (or other iterable)
        for validator in validators:
            if callable(validator):
                result = validator(value, error_callback, validator_fmt_str)
            else:  # validator is a value, not a function
                result = value == validator
            if result:
                break
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

    :return: **True** if all of the validators pass, **False** if they all fail.
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

    :return: **True** if none of the validators pass, **False** if they any of them pass.
    """
    result = False

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):  # list of validators (or other iterable)
        for validator in validators:
            if callable(validator):
                result = validator(value, silent_error, validator_fmt_str)
            else:   # validator is a value, not a function
                result = value == validator
            if result:
                break
    elif callable(validators):  # single validator function
        result = validators(value, silent_error, validator_fmt_str)
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

    :return: **True** if the input passed validation, else **False**
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
class Validator(object):
    # Abstract base class for validation classes
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, value, error_callback, validator_fmt_str):
        pass


class LengthValidator(Validator):
    """
    check a value is in between a length range (open interval). For exact length match set min and max lengths
    to the same value.

    :param min_len: the minimum required length for the input. If None (the default), no minimum length is checked.
    :param max_len: the maximum required length for the input. If None (the default), no maximum length is checked.

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, min_len=None, max_len=None):
        self._min_len = min_len
        self._max_len = max_len

    def __call__(self, value, error_callback, validator_fmt_str):
        try:
            val_len = len(value)
        except (TypeError):
            print('LengthValidator: value "{}" does not support __len__.'.format(value), file=sys.stderr)
            return False

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
        return 'LengthValidator(min_len=%s, max_len=%s)' % (self._min_len, self._max_len)


class EqualToValidator(Validator):
    """
    check if a value is an exact value

    :param value: the value to match

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, value):
        self._value = value

    def __call__(self, value, error_callback, validator_fmt_str):
        condition1 = (self._value is None or value == self._value)

        if condition1:
            return True
        else:
            error_callback(validator_fmt_str, 'value', 'not equal to {}'.format(self._value))
            return False

    def __repr__(self):
        return 'EqualToValidator(value=%s)' % self._value


class RangeValidator(Validator):
    """
    check if a value is in between a minimum and maximum value (open interval). The value can be of any type as long
    as the __ge__ and __le__ comparison functions are defined.

    :param min_val: The minimum allowed value (i.e. value must be <= min_val). If None (the default), no minimum value is checked.
    :param max_val: The maximum allowed value (i.e. value must be >= min_val). If None (the default), no maximum value is checked.

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, min_val=None, max_val=None):
        self._min_val = min_val
        self._max_val = max_val

    def __call__(self, value, error_callback, validator_fmt_str):
        try:
            min_condition = (self._min_val is None or value >= self._min_val)
        except (TypeError):
            print('RangeValidator: value "{}" does not support __ge__.'.format(value), file=sys.stderr)
            return False

        try:
            max_condition = (self._max_val is None or value <= self._max_val)
        except (TypeError):
            print('RangeValidator: value "{}" does not support __ge__.'.format(value), file=sys.stderr)
            return False

        if min_condition and max_condition:
            return True
        elif not min_condition:
            error_callback(validator_fmt_str, value, 'too low (min_val={})'.format(self._min_val))
            return False
        else:
            error_callback(validator_fmt_str, value, 'too high (max_val={})'.format(self._max_val))
            return False

    def __repr__(self):
        return 'RangeValidator(min_val=%s, max_val=%s)' % (self._min_val, self._max_val)


class ChoiceValidator(Validator):
    """
    check if a value is in a list of choices. Note: if choices is mutable, it can be changed after the instance is created.

    :param choices: an iterable (tuple, list, or set) containing the allowed set of choice for the value.

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, choices):
        # note: if choices is mutable, the choices can change after instantiation
        self._choices = put_in_a_list(choices)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = value in self._choices

        if result:
            return True
        else:
            choice_strs = [str(c) for c in self._choices]
            error_callback(validator_fmt_str, 'value', 'must be one of: {}'.format(', '.join(choice_strs)))
            return False

    def __repr__(self):
        return 'ChoiceValidator(choices={})'.format(self._choices)


class NoneOfValidator(Validator):
    """
    check if a value is not in a set of validators. Note: if choices is mutable, it can be changed after the instance is created.

    :param validators: an iterable list of validators that should not match the input value.

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, validators):
        self._validators = validators

    def __call__(self, value, error_callback, validator_fmt_str):
        result = not_in(value, self._validators, error_callback, validator_fmt_str)

        # error callback handled within not_in call
        return result

    def __repr__(self):
        return 'NoneOfValidator(validators={})'.format(self._validators)


class AnyOfValidator(Validator):
    """
    check if a value matches any of a set of validators (OR operation). Note: if choices is mutable, it can be changed after the instance is created.

    :param validators: an iterable list of validators. When the validators is called, return True once any of the validators matches.

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, validators):
        self._validators = validators

    def __call__(self, value, error_callback, validator_fmt_str):
        result = in_any(value, self._validators, error_callback, validator_fmt_str)
        return result

    def __repr__(self):
        return 'AnyOfValidator(validators={})'.format(self._validators)


class IsFileValidator(Validator):
    """
    check is a string is the name of an existing filename

    :param value: the filename to verify

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self):
        pass

    def __call__(self, value, error_callback, validator_fmt_str):
        if os.path.isfile(value):
            return True
        else:
            error_callback(validator_fmt_str, value, '{} is not a valid file'.format(value))
            return False

    def __repr__(self):
        return 'IsFileValidator()'


class SimpleValidator(Validator):
    """
    check if a value matches any function that takes a single value as input and returns a Boolean. Used to wrap
    functions (e.g. validus validation functions see: [https://shopnilsazal.github.io/validus/].) Can also be used with func.partial [https://docs.python.org/3/library/functools.html]
    to wrap validation functions that take more complex parameters.

    :param validators: an iterable list of validators. When the validators is called, return True once any of the validators matches.
    :param name: an optional string to use for the validator name in error messages

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, validator_func, name='SimpleValidator value'):
        self._validator = validator_func
        self._name = None

    def __call__(self, value, error_callback, validator_fmt_str):
        result = self._validator(value)

        if not result:
            error_callback(validator_fmt_str, value, 'is not a valid {}'.format(self._name))

        return result

    def __repr__(self):
        return 'SimpleValidator(validators={})'.format(self._validator)


class RegexValidator(Validator):
    """
    check if a value matches a regular expression.

    :param pattern: the regular expression to match
    :param regex_desc: a human readable string to use for the regex (used for error messages)

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, pattern, regex_desc=None):
        self._regex = pattern
        self._regex_desc = regex_desc

    def __call__(self, value, error_callback, validator_fmt_str):
        try:
            result = re.search(self._regex, value)
        except (TypeError):
            print('RegexValidator: expected string or bytes-like object. "{}" not compatible.'.format(value), file=sys.stderr)
            return False

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

    :param min_len: the minimum allowed password length. Defaults to 1
    :param max_len: the maximum password length. Defaults to 64
    :param min_lower: the minimum number of lower case letters. Defaults to None
    :param min_upper: the minimum number of upper case letters. Defaults to None
    :param min_digits: the minimum number of digits. Defaults to None
    :param min_puncts: the minimum number of punctuation characters. Defaults to None
    :param allowed: a string containing the allowed characters in the password. Defaults to upper and lower case ascii
        letters, plus digits, plus punctuation characters
    :param disallowed: a string containing characters not allowed in the password. Defaults to None

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, min_len=None, max_len=None, min_lower=0, min_upper=0, min_digits=0, min_puncts=0,
                 allowed=None, disallowed=None):
        self._valid_chars = set(string.ascii_letters + string.digits + string.punctuation)
        self._min_len = min_len
        self._max_len = max_len
        self._min_lower = min_lower
        self._min_upper = min_upper
        self._min_digits = min_digits
        self._min_puncts = min_puncts

        if disallowed is not None:
            self._disallowed = set(disallowed)
        else:
            self._disallowed = set()

        if allowed is not None:
            self._valid_chars = set(allowed)

        self._valid_chars -= self._disallowed

    def __call__(self, value, error_callback, validator_fmt_str):
        if isstring(value) is False:
            print('PasswordValidator: value "{}" is not a string.'.format(value), file=sys.stderr)
            return False

        if len(set(value) - self._valid_chars):
            error_callback(validator_fmt_str, 'password', 'cannot contain any of the following characters: {}'.format(
                               set(value) - self._valid_chars))
            return False

        if self._min_len is not None and (len(value)) < self._min_len:
            error_callback(validator_fmt_str, 'password',
                           'too short (minimum length is {})'.format(self._min_len))
            return False

        if self._max_len and len(value) > self._max_len:
            error_callback(validator_fmt_str, 'password', 'too long (maximum length is {})'.format(self._max_len))
            return False

        if self._min_lower and len([c for c in value if c in string.ascii_lowercase]) < self._min_lower:
            error_callback(validator_fmt_str, 'password',
                           'too few lower case characters (minimum is {})'.format(self._min_lower))
            return False

        if self._min_upper and len([c for c in value if c in string.ascii_uppercase]) < self._min_upper:
            error_callback(validator_fmt_str, 'password', 'too few upper case characters (minimum is {})'.format(self._min_upper))
            return False

        if self._min_digits and len([c for c in value if c in string.digits]) < self._min_digits:
            error_callback(validator_fmt_str, 'password', 'too few digit characters (minimum is {})'.format(self._min_digits))
            return False

        if self._min_puncts and len([c for c in value if c in string.punctuation]) < self._min_puncts:
            error_callback(validator_fmt_str, 'password', 'too few punctuation characters (minimum is {})'.format(self._min_puncts,
                                                                                                                  set(string.punctuation) - self._disallowed))
            return False

        return True

    def __repr__(self):
        return 'PasswordValidator(allowed=%r, min_len=%r, max_len=%r, min_lowercase=%r, min_uppercase=%r, min_digits=%r, min_puncts=%r)' %\
               (self._valid_chars, self._min_len, self._max_len, self._min_lower, self._min_upper, self._min_digits, self._min_puncts)


class ListValidator(Validator):
    """
    Run a set of validators on a list.

    :param len_validator: a validator to run on the list length.
    :param elem_validators: a single or list of validators to apply to the elements of the list.

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, len_validator=None, elem_validators=None):
        self._len_validator = len_validator
        self._elem_validators = elem_validators

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
