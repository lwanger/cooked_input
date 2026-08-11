"""
This file contains validator classes for cooked_input

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""

from __future__ import annotations

import os
import sys
import string
import re

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import Any, Callable

from ._typing import ErrorCallback
from .error_callbacks import print_error, silent_error, DEFAULT_VALIDATOR_ERROR
from .input_utils import put_in_a_list, isstring


def in_any(value: Any, validators: Any, error_callback: ErrorCallback,
           validator_fmt_str: str) -> bool:
    """
    return **True** if the value passes any of the ``validators`` - OR's the list of supplied `validators <validators.html>`_.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the `validators <validators.html>`_ to use.
    :param error_callback: a function called when an error occurs during validation
    :param validator_fmt_str: format string for validation errors

    :return: boolean **True** if any of the validators pass, **False** if they all fail.

    An empty iterable of validators passes vacuously, the same as passing **None**.
    """

    if validators is None:
        return True

    # Fixing: `result` used to be assigned only inside the branches below, so an empty
    # iterable -- whose loop body never runs -- left it unbound and raised
    # UnboundLocalError. Seeding it with the "no validators supplied" answer makes
    # in_any([]) agree with in_any(None) and with in_all([]).
    result = True

    if isinstance(validators, Iterable):  # list of validators (or other iterable)
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


def in_all(value: Any, validators: Any, error_callback: ErrorCallback,
           validator_fmt_str: str) -> bool:
    """
    return **True** if the value passes all of the validators - AND's the list of supplied `validators <validators.html>`_.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the `validators <validators.html>`_ to use.
    :param error_callback: a function called when an error occurs during validation
    :param validator_fmt_str: format string to pass to the error callback routine for formatting the error.

    :return: boolean **True** if all of the validators pass, **False** if they all fail.
    """

    if validators is None:
        result = True
    elif isinstance(validators, Iterable):
        result = all(validator(value, error_callback, validator_fmt_str) for validator in validators)
    elif callable(validators):
        result = validators(value, error_callback, validator_fmt_str)
    else:
        result = value == validators

    return result


def not_in(value: Any, validators: Any, error_callback: ErrorCallback,
           validator_fmt_str: str) -> bool:
    """
    return **True** if the value does not pass any of the validators - NOT's the list of supplied `validators <validators.html>`_.

    :param value: the input value to validate
    :param validators: an iterable (list or tuple) containing the `validators <validators.html>`_ to use.
    :param error_callback: a function called when an error occurs during validation
    :param validator_fmt_str: format string to pass to the error callback routine for formatting the error.

    :return: boolean **True** if none of the validators pass, **False** if they any of them pass.

    No validators -- **None** or an empty iterable -- passes vacuously: there is nothing
    for the value to match.
    """
    result = False

    if validators is None:
        # Fixing: this branch used to set `result = True`, which is read below as "a
        # validator matched". not_in(value, None) therefore rejected every value and
        # reported "value cannot match <value>", naming a validator that does not
        # exist -- so NoneOfValidator(None) refused everything while AnyOfValidator(None)
        # accepted everything. Nothing supplied means nothing matched.
        return True
    elif isinstance(validators, Iterable):  # list of validators (or other iterable)
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
        error_callback(validator_fmt_str, value, 'value cannot match {}'.format(value))
        return False


def validate(value: Any, validators: Any, error_callback: ErrorCallback = print_error,
             validator_fmt_str: str = DEFAULT_VALIDATOR_ERROR) -> bool | None:
    """
    return **True** is a value passes validation.

    :param value: the value to validate
    :param validators: an iterable (list or tuple) of `validators <validators.html>`_ to run on ``value``
    :param error_callback: a function called when an error occurs during validation
    :param validator_fmt_str: format string to pass to the error callback routine for formatting the error

    :return: **True** if the input passed validation, else **False**

    .. note::
        Unlike :func:`in_any`, :func:`in_all` and :func:`not_in`, which all treat "no
        validators" as passing, an empty iterable here returns **None** and **None**
        raises `TypeError`. Hence the ``bool | None`` return type. See issue #71.
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
class Validator(metaclass=ABCMeta):
    """
    Abstract base class for validators. Subclasses must implement :meth:`__call__`, which
    returns **True** if the value passes validation and **False** if it does not.

    Fixing: this used to say ``__metaclass__ = ABCMeta``, the Python 2 spelling, which on
    Python 3 is an inert class attribute. Nothing was enforced -- ``Validator()`` instantiated
    happily and a subclass that forgot ``__call__`` returned **None** from every check, which
    reads as a validation failure, instead of failing loudly. ``__init__`` is deliberately not
    abstract, so a subclass that only implements ``__call__`` still works.
    """
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        pass


class LengthValidator(Validator):
    """
    check the length of a value is in a range (open interval). For exact length match set ``min_len`` and ``max_len`` lengths
    to the same value.

    :param min_len: the minimum required length for the input. If **None** (default), no minimum length is checked.
    :param max_len: the maximum required length for the input. If **None** (default), no maximum length is checked.

    :return: **True** if the input passed validation

    Example::

        lv = LengthValidator(min_len=3, max_len=5)
        result = get_string(prompt="Enter a 3 to 5 char string", validators=lv)

    """
    def __init__(self, min_len: int | None = None, max_len: int | None = None) -> None:
        self._min_len = min_len
        self._max_len = max_len

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
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

    def __repr__(self) -> str:
        return 'LengthValidator(min_len=%s, max_len=%s)' % (self._min_len, self._max_len)


class EqualToValidator(Validator):
    """
    check if a value is equal to a specified value.

    :param value: the value to match

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self, value: Any) -> None:
        self._value = value

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        condition1 = (self._value is None or value == self._value)

        if condition1:
            return True
        else:
            error_callback(validator_fmt_str, value, 'value not equal to {}'.format(self._value))
            return False

    def __repr__(self) -> str:
        return 'EqualToValidator(value=%s)' % self._value


class RangeValidator(Validator):
    """
    check if a value is in a specified range (open interval.) The value can be of any type as long
    as the ``__ge__`` and ``__le__`` comparison functions are defined.

    :param min_val: The minimum allowed value (i.e. ``value`` must be >= ``min_val``). If **None** (the default), no minimum value is checked.
    :param max_val: The maximum allowed value (i.e. ``value`` must be <= max_val). If **None** (the default), no maximum value is checked.

    :return: **True** if the input passed validation, else **False**

    Example::

        rv = RangeValidator(min_val=1), max_val=10)
        result = get_int(prompt="Enter a number (1 to 10)", validators=rv)

    """
    def __init__(self, min_val: Any = None, max_val: Any = None) -> None:
        self._min_val = min_val
        self._max_val = max_val

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
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

    def __repr__(self) -> str:
        return 'RangeValidator(min_val=%s, max_val=%s)' % (self._min_val, self._max_val)


class ChoiceValidator(Validator):
    """
    check if a value is in a set of choices.

    :param choices: an iterable (tuple, list, or set) containing the allowed set of choices for the value.

    :return: **True** if the input passed validation, else **False**


    Example::

        colors = ["red", "green", "blue"]
        cv = ChoiceValidator(colors]
        result = get_string(prompt="Enter a color", validators=cv)

    """
    def __init__(self, choices: Any) -> None:
        # note: if choices is mutable, the choices can change after instantiation
        self._choices = put_in_a_list(choices)

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        result = value in self._choices

        if result:
            return True
        else:
            choice_strs = [str(c) for c in self._choices]
            error_callback(validator_fmt_str, value, 'value must be one of: {}'.format(', '.join(choice_strs)))
            return False

    def __repr__(self) -> str:
        return 'ChoiceValidator(choices={})'.format(self._choices)


class NoneOfValidator(Validator):
    """
    check if a value does not pass validation for a list of `validators <validators.html>`_ (NOT operation).

    :param validators: a list of `validators <validators.html>`_ that should not pass
        validation on the input value

    :return: **True** if the input passed validation, else **False**

    .. note::
        if ``choices`` is mutable, it can be changed after the instance is created.

    Example::

        rv1 = RangeValidator(min_val=1, max_val=3)
        rv2 = EqualToValidator(7)
        nv = NoneOfValidator([rv1, rv2])
        prompt_str = "Enter a number (not between 1 and 3, and not 7)"
        result = get_int(prompt=prompt_str, validators = nv)

    """
    def __init__(self, validators: Any) -> None:
        self._validators = validators

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        result = not_in(value, self._validators, error_callback, validator_fmt_str)

        # error callback handled within not_in call
        return result

    def __repr__(self) -> str:
        return 'NoneOfValidator(validators={})'.format(self._validators)


class AnyOfValidator(Validator):
    """
    check if a value matches any of a set of `validators <validators.html>`_ (OR operation).

    :param validators: a list of `validators <validators.html>`_. Returns **True**
        once any of the `validators <validators.html>`_ passes.

    :return: **True** if the input passed validation, else **False**

    .. note::
        if ``choices`` is mutable, it can be changed after the instance is created.

    Example::

        rv1 = RangeValidator(min_val=1, max_val=3)
        rv2 = EqualToValidator(7)
        nv = AnyOfValidator([rv1, rv2])
        prompt_str = "Enter a number (between 1 and 3, or 7)"
        result = get_int(prompt=prompt_str, validators = nv)

    """
    def __init__(self, validators: Any) -> None:
        self._validators = validators

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        result = in_any(value, self._validators, error_callback, validator_fmt_str)
        return result

    def __repr__(self) -> str:
        return 'AnyOfValidator(validators={})'.format(self._validators)


class IsFileValidator(Validator):
    """
    check is a string is the name of an existing filename

    :param value: the filename to verify

    :return: **True** if the input passed validation, else **False**
    """
    def __init__(self) -> None:
        pass

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        if os.path.isfile(value):
            return True
        else:
            error_callback(validator_fmt_str, value, '{} is not a valid file'.format(value))
            return False

    def __repr__(self) -> str:
        return 'IsFileValidator()'


class SimpleValidator(Validator):
    """
    use a simple function as a `validator <validators.html>`_. ``validator_func`` is any callable that takes a single
    value as input and returns **True** if the value passes (and **False** otherwise.) Used to wrap boolean
    validation functions, whether your own or from a third-party library. Can also be used with `func.partial
    <https://docs.python.org/3/library/functools.html#partial-objects>`_ to wrap validation functions that take more complex parameters.

    :param validator_func: a function (or other callable) called to validate the value
    :param name: an optional string to use for the validator name in error messages

    :return: **True** if the input passed validation, else **False**

    Example::

        def is_even(value):
            return True if (value % 2) == 0 else False

        sv = SimpleValidator(is_even, "EvenNumberValidator")
        result = get_int(prompt="Enter an even number", validators = sv)
    """
    def __init__(self, validator_func: Callable[[Any], bool],
                 name: str = 'SimpleValidator value') -> None:
        self._validator = validator_func
        # Fixing: this was `self._name = None`, which threw the caller's name away,
        # so every failure message read "is not a valid None" and the documented
        # `name` parameter did nothing.
        self._name = name

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        result = self._validator(value)

        if not result:
            error_callback(validator_fmt_str, value, 'is not a valid {}'.format(self._name))

        return result

    def __repr__(self) -> str:
        return 'SimpleValidator(validators={})'.format(self._validator)


class RegexValidator(Validator):
    r"""
    check if a value matches a `regular expression <https://docs.python.org/3/library/re.html?highlight=re#module-re>`_.

    :param pattern: the `regular expression <https://docs.python.org/3/library/re.html?highlight=re#module-re>`_ to match
    :param regex_desc: a human readable string to use for the regular expression (used for error messages)

    :return: **True** if the input passed validation, else **False**

    Example::

        rv = RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='phone number')
        result = get_string(prompt="Enter a phone number", validators = rv)

    """
    def __init__(self, pattern: str | re.Pattern[str], regex_desc: str | None = None) -> None:
        self._regex = pattern
        self._regex_desc = regex_desc

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
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

    def __repr__(self) -> str:
        return 'RegexValidator(regex={})'.format(self._regex)


class PasswordValidator(Validator):
    """
    validate a password string.

    :param min_len: the minimum allowed password length (default=1)
    :param max_len: the maximum password length (default=64)
    :param min_lower: the minimum number of lower case letters (default=``None``)
    :param min_upper: the minimum number of upper case letters (default=``None``)
    :param min_digits: the minimum number of digits (default=``None``)
    :param min_puncts: the minimum number of punctuation characters (default=``None`)
    :param allowed: a string containing the allowed characters in the password. Default is upper and lower case ascii
        letters, plus digits, plus punctuation characters
    :param disallowed: a string containing characters not allowed in the password (default=``None``)

    :return: **True** if the input passed validation, else **False**

    Example::

        pv = PasswordValidator(min_len=5, min_lower=2, min_upper=2, min_digits=1, min_puncts=1)
        result = ci.get_string(prompt="Enter a password", validators=pv, hidden=True)

    """
    def __init__(self, min_len: int | None = None, max_len: int | None = None, min_lower: int = 0,
                 min_upper: int = 0, min_digits: int = 0, min_puncts: int = 0,
                 allowed: str | None = None, disallowed: str | None = None) -> None:
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

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
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

    def __repr__(self) -> str:
        return 'PasswordValidator(allowed=%r, min_len=%r, max_len=%r, min_lowercase=%r, min_uppercase=%r, min_digits=%r, min_puncts=%r)' %\
               (self._valid_chars, self._min_len, self._max_len, self._min_lower, self._min_upper, self._min_digits, self._min_puncts)


class ListValidator(Validator):
    """
    Run a set of `validators <validators.html>`_ on a list.

    :param len_validators: a list of  `validators <validators.html>`_ to run on the length of the ``value``
        list. if **None** (default) no validation is done on the list length.
    :param elem_validators: a list of `validators <validators.html>`_ to apply to the
        elements of the list.
    :param len_validator_fmt_str: a format string to use as an error message is the length of the ``value`` string
        does not pass the length validation (``len_validators``). If **None** (default), ``validator_fmt_str`` is used
        from the call to the validator.

    :return: **True** if the input passed validation, else **False**

    .. note::

        ``len_validators`` is usually an instance of :class:`EqualToValidator` for a list of a specific length, or
        :class:`RangeValidator` for a list whose length is in a range. :class:`LengthValidator` is not used as the ``value``
        passed to the validator is the length of the list, not the list itself.

    Example::

        colors = ['red', 'green', 'blue']
        len_validator = ci.RangeValidator(min_val=2, max_val=4)
        lvfs="List length {error_content} ({value})"
        elem_validator = ci.ChoiceValidator(colors)
        prompt_str = "Enter a list of 2 to 4 colors"
        lv = ci.ListValidator(len_validators=len_validator, elem_validators=elem_validator, len_validator_fmt_str=lvfs)
        result = ci.get_list(prompt=prompt_str, validators=lv)

    """
    def __init__(self, len_validators: Any = None, elem_validators: Any = None,
                 len_validator_fmt_str: str | None = None) -> None:
        self._len_validators = len_validators
        self._elem_validators = elem_validators
        self._len_validator_fmt_str = len_validator_fmt_str

    def __call__(self, value: Any, error_callback: ErrorCallback, validator_fmt_str: str) -> bool:
        if self._len_validators:
            if self._len_validator_fmt_str is None:
                use_llvfs = validator_fmt_str
            else:
                use_llvfs = self._len_validator_fmt_str

            result = validate(len(value), self._len_validators, error_callback, use_llvfs)

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

    def __repr__(self) -> str:
        return 'ListValidator()'.format()
