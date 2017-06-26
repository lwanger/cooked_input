"""
get_input module to get values from the command line.

This file contains validator classes for io_get_input

For more validators: look at using validus:
    https://shopnilsazal.github.io/validus/readme.html

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
import string
import re


def compose(value, funcs):
    # compose functions and return the result: compose(value, [f1,f2,f3]) = f3(f2(f1(value)))
    result = None
    if callable(funcs):
        result = funcs(value)
    else:
        for func in funcs:
            if not result:
                result = func(value)
            else:
                result = func(result)
    return result


def in_any(value, validators):
    """
    return True if the value passes any of the validators - OR's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :return: True if any of the validators pass, False if they all fail.
    """

    if isinstance(validators, collections.Iterable):
        result = any(validator(value) for validator in validators)
    elif validators is None:
        result = True
    else:
        result = validators(value)

    return result

import collections


def in_all(value, validators):
    """
    return True if the value passes all of the validators - AND's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :return: True if all of the validators pass, False if they all fail.
    """

    if isinstance(validators, collections.Iterable):
        result = all(validator(value) for validator in validators)
    elif validators is None:
        result = True
    else:
        result = validators(value)

    return result


def not_in(value, validators):
    """
    return True if the value does not pass any of the validators - NOT's the list of supplied validators.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the validators to use.
    :return: True if none of the validators pass, False if they any of them pass.
    """
    result = in_any(value, validators)
    return not result


def validate(value, validators=None):
    """
    Run validators on a value.

    :param value: the value to validate.
    :param validators: list of validators to run on the value.
    :return: True if the input passed validation, else False
    """
    return compose(value, validators)


####
#### Validators:
####
# class Validator(metaclass=ABCMeta): # introduced in Python 3
class Validator(object):
    # Abstract base class for validation classes
    def __init__(self):
        pass

    # @abstractmethod   # introduced in Python 3
    def __call__(self, value):
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

    def __call__(self, value):
        # TypeError thrown if value does not implement __len__
        val_len = len(value)
        condition1 = (self._length is None or val_len == self._length)
        return True if condition1 else False

    def __repr__(self):
        return 'ExactLengthValidator(value=%s)' % (self._length)


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

    def __call__(self, value):
        # TypeError thrown if value does not implement __len__
        val_len = len(value)
        min_condition = (self._min_len is None or val_len >= self._min_len)
        max_condition = (self._max_len is None or val_len <= self._max_len)
        return True if min_condition and max_condition else False

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

    def __call__(self, value):
        condition1 = (self._value is None or value == self._value)
        return True if condition1 else False

    def __repr__(self):
        return 'ExactValueValidator(value=%s)' % (self._value)


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

    def __call__(self, value):
        min_condition = (self._min_val is None or value >= self._min_val)
        max_condition = (self._max_val is None or value <= self._max_val)
        return True if min_condition and max_condition else False

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
        self._choices = choices
        super(InChoicesValidator, self).__init__(**kwargs)

    def __call__(self, value):
        result = value in self._choices
        return result

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

    def __call__(self, value):
        # result = value in self._choices
        result = not_in(value, self._validators)
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

    def __call__(self, value):
        # result = value in self._choices
        result = in_any(value, self._validators)
        return result

    def __repr__(self):
        return 'InAnyValidator(validators={})'.format(self._validators)


class RegexValidator(Validator):
    """
    check if a value matches a regular expression.

    :param regex: the regular expression to match.
    :param kwargs: kwargs: no kwargs are currently supported.
    """
    def __init__(self, regex, **kwargs):
        # note: if choices is mutable, the choices can change after instantiation
        self._regex = regex
        super(RegexValidator, self).__init__(**kwargs)

    def __call__(self, value):
        result = re.search(self._regex, value)
        return True if result else False

    def __repr__(self):
        return 'RegexValidator(regegx={})'.format(self._regex)


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
        self.valid_chars = set(string.ascii_letters + string.digits +  string.punctuation)
        # disallowed_chars = None

        self.min_length = min_length
        self.max_length = max_length
        self.min_lower = min_lower
        self.min_upper = min_upper
        self.min_digits = min_digits
        self.min_puncts = min_puncts

        if allowed is not None:
            self.valid_chars = set(allowed)
        elif disallowed is not None:
            # disallowed_chars = disallowed
            self.valid_chars -= set(disallowed)

        super(PasswordValidator, self).__init__(**kwargs)

    def __call__(self, value):
        if len(set(value) - self.valid_chars):
            return False

        if self.min_length and len(value) < self.min_length:
            return False

        if self.max_length and len(value) > self.max_length:
            return False

        if self.min_lower and len([c for c in value if c in string.ascii_lowercase]) < self.min_lower:
            return False

        if self.min_upper and len([c for c in value if c in string.ascii_uppercase]) < self.min_upper:
            return False

        if self.min_digits and len([c for c in value if c in string.digits]) < self.min_digits:
            return False

        if self.min_puncts and len([c for c in value if c in string.punctuation]) < self.min_puncts:
            return False

        return True

    def __repr__(self):
        return 'PasswordValidator(allowed=%r, min_length=%r, max_length=%r, min_lowercase=%r, min_uppercase=%r, min_digits=%r, min_puncts=%r)' %\
               (self.valid_chars, self.min_length, self.max_length, self.min_lower, self.min_upper, self.min_digits, self.min_puncts)