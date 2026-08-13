"""
Convenience functions for getting values from the command line.

Each of these builds a :class:`GetInput` with the convertor, cleaners and prompt suited to one
type and calls it, so ``get_int()`` is the short way to say ``GetInput(convertor=IntConvertor(),
...).get_input()``. Most users never need anything else; the machinery they wrap lives in
``get_input.py``.

Split out of ``get_input.py``, which had grown past 1100 lines holding both.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""


from __future__ import annotations

import collections.abc
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, overload

from ._typing import CleanerArg, CommandsArg, ErrorCallback, GetInputValidatorArg
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .validators import Validator, RangeValidator, LengthValidator
from .convertors import Convertor, IntConvertor, FloatConvertor, BooleanConvertor, DateConvertor
from .convertors import YesNoConvertor, ListConvertor, DecimalConvertor
from .cleaners import StripCleaner, RegexCleaner, RemoveCleaner
from .input_utils import isstring, put_in_a_list
from .get_input import GetInput, ProcessValueResponse
# GetInputCommand is not used in the code below, only in the ``CommandsArg`` annotation -- but
# that alias leaves the class name quoted (see ``_typing``), and a quoted forward reference is
# resolved in the module that *uses* the alias. get_table.py carries this same import for the
# same reason; without it sphinx_autodoc_typehints fails the -W docs build with "Cannot resolve
# forward reference" for every get_* function here.
from .get_input import GetInputCommand  # noqa: F401


#############################
### Convenience Functions ###
#############################

def _add_range_validator(validators: GetInputValidatorArg, minimum: Any,
                         maximum: Any) -> GetInputValidatorArg:
    """
    Add a :class:`RangeValidator` for ``minimum``/``maximum`` to the caller's validators.

    :param validators: whatever the caller passed for ``validators``
    :param minimum: the low end of the range, or **None** for no minimum
    :param maximum: the high end of the range, or **None** for no maximum

    :return: the validators to hand to :class:`GetInput`, unchanged when no range was asked for

    ``get_int``, ``get_float`` and ``get_date`` all offer ``minimum``/``maximum``, and each had its own
    copy of this. Sharing it is what makes the fix below hold for all three at once.
    """
    if minimum is None and maximum is None:
        return validators

    range_validator = RangeValidator(min_val=minimum, max_val=maximum)

    if validators is None:
        return range_validator
    elif callable(validators):
        return [validators, range_validator]

    # Fixing: this was `validators + [range_validator]`, which needs a list on the left -- so a
    # tuple of validators raised "can only concatenate tuple (not list) to tuple" the moment a
    # minimum or maximum was also given. get_string accepts a tuple, since it extends a list
    # instead, so the two disagreed about what `validators` could be. put_in_a_list is the helper
    # the package already has for exactly this.
    return put_in_a_list(validators) + [range_validator]

def get_input(cleaners: CleanerArg = None, convertor: Convertor | None = None,
              validators: GetInputValidatorArg = None, *,
              prompt: str = '',
              required: bool = True,
              default: Any = None,
              default_str: str | None = None,
              hidden: bool = False,
              retries: int | None = None,
              commands: CommandsArg = None,
              error_callback: ErrorCallback = print_error,
              convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
              validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> Any:
    """
    Get a value from the user, applying a convertor of your choosing.

    Typical use::

        ci.get_input(prompt="How many?", convertor=ci.IntConvertor())

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param convertor: the `convertor <convertors.html>`_ to apply to the cleaned value
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated input. The return type is **Any** because it is
        whatever ``convertor`` produces -- an `int` for :class:`IntConvertor`, a `datetime` for
        :class:`DateConvertor`, and so on. With no convertor the value comes back as the `str`
        that was typed.

    :raises TypeError: if given an option this function does not have

    Convenience function to create a :class:`GetInput` instance and call its `get_input` function. See
    :func:`GetInput.get_input` for more details on the options, all of which are keyword-only.
    """
    gi = GetInput(cleaners, convertor, validators, prompt=prompt, required=required, default=default,
                  default_str=default_str, hidden=hidden, retries=retries, commands=commands,
                  error_callback=error_callback, convertor_error_fmt=convertor_error_fmt,
                  validator_error_fmt=validator_error_fmt)
    return gi.get_input()


def process_value(value: Any, cleaners: CleanerArg = None, convertor: Convertor | None = None,
                  validators: GetInputValidatorArg = None, error_callback: ErrorCallback = print_error,
                  convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
                  validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> ProcessValueResponse:
    """
    :param value: the value to process
    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value
    :param convertor: the `convertor <convertors.html>`_ to apply to the cleaned value
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param error_callback: a callback function to call when an error is encountered. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string to use for convertor errors. Defaults to **DEFAULT_CONVERTOR_ERROR**
    :param validator_error_fmt: format string to use for validator errors. Defaults to **DEFAULT_VALIDATOR_ERROR**

    :return: a **ProcessValueResponse** namedtuple of ``(valid, value)``. ``value`` is typed
        **Any** because it is whatever ``convertor`` produces; it is **None** when ``valid``
        is **False**.

    Convenience function to create a :class:`GetInput` instance and call its process_value function. See
    :func:`GetInput.process_value` for more details. See  :class:`GetInput` for more information on the
    `error_callback`, `convertor_error_fmt`, and `validator_error_fmt` parameters.
    """
    gi = GetInput(cleaners, convertor, validators, error_callback=error_callback,
                  convertor_error_fmt=convertor_error_fmt, validator_error_fmt=validator_error_fmt)
    return gi.process_value(value)


# A blank response only returns None when required is False, so the default call cannot. The pair
# below says that to a type checker; see the note above get_input's `if not self.required` return.
@overload
def get_string(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
               min_len: int | None = ..., max_len: int | None = ..., *,
               prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
               default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
               commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
               convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> str: ...
@overload
def get_string(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
               min_len: int | None = ..., max_len: int | None = ..., *,
               prompt: str = ..., required: Literal[False], default: Any = ...,
               default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
               commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
               convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> str | None: ...
def get_string(cleaners: CleanerArg = (StripCleaner()), validators: GetInputValidatorArg = None,
               min_len: int | None = None, max_len: int | None = None, *,
               prompt: str = 'Enter some text',
               required: bool = True,
               default: Any = None,
               default_str: str | None = None,
               hidden: bool = False,
               retries: int | None = None,
               commands: CommandsArg = None,
               error_callback: ErrorCallback = print_error,
               convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
               validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> str | None:
    """
    Get a string value from the user.

    Typical use::

        ci.get_string(prompt="What is your favorite color?")

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param min_len: the minimum allowable length for the string. No minimum length if None (default)
    :param max_len: the maximum allowable length for the string. No maximum length if None (default)
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen -- useful for passwords
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: accepted and ignored -- this function applies no convertor, so there
        are no conversion errors to word. It is accepted so that the whole option set stays uniform
        across the ``get_*`` functions. For the rare case of converting a string to a string-like
        type, such as `bytes` or `bytearray`, use :func:`get_input` with a `convertor
        <convertors.html>`_; there the format string does fire.
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated string

    :raises TypeError: if given an option this function does not have

    Convenience function to get a string value. Every parameter from ``prompt`` onwards is a
    keyword-only :class:`GetInput` option; most calls use one or two.
    """
    use_validators: list[Any] = []
    if min_len is not None or max_len is not None:
        use_validators.append(LengthValidator(min_len=min_len, max_len=max_len))

    if isinstance(validators, Validator):
        use_validators.append(validators)
    elif validators is not None:
        use_validators.extend(put_in_a_list(validators))

    result = GetInput(cleaners, None, use_validators, prompt=prompt, required=required, default=default,
                      default_str=default_str, hidden=hidden, retries=retries, commands=commands,
                      error_callback=error_callback, convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_int(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
            minimum: int | None = ..., maximum: int | None = ..., base: int = ..., *,
            prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
            default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
            commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
            convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> int: ...
@overload
def get_int(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
            minimum: int | None = ..., maximum: int | None = ..., base: int = ..., *,
            prompt: str = ..., required: Literal[False], default: Any = ...,
            default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
            commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
            convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> int | None: ...
def get_int(cleaners: CleanerArg = None, validators: GetInputValidatorArg = None, minimum: int | None = None,
            maximum: int | None = None, base: int = 10, *,
            prompt: str = 'Enter a whole (integer) number',
            required: bool = True,
            default: Any = None,
            default_str: str | None = None,
            hidden: bool = False,
            retries: int | None = None,
            commands: CommandsArg = None,
            error_callback: ErrorCallback = print_error,
            convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
            validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> int | None:
    """
    Get a whole number from the user.

    Typical use::

        ci.get_int(prompt="How old are you?", minimum=0)

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param minimum: minimum value allowed. Use None (default) for no minimum value.
    :param maximum: maximum value allowed. Use None (default) for no maximum value.
    :param base: Convert a string in radix base to an integer. Base defaults to 10.
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated int value

    :raises TypeError: if given an option this function does not have

    Convenience function to get an integer value. See the documentation for the Python
    `int <https://docs.python.org/3/library/functions.html#int>`_ builtin function for further description
    of the `base` parameter. Every parameter from ``prompt`` onwards is a keyword-only
    :class:`GetInput` option; most calls use one or two.
    """
    val_list = _add_range_validator(validators, minimum, maximum)
    result = GetInput(cleaners, IntConvertor(base=base), val_list, prompt=prompt, required=required,
                      default=default, default_str=default_str, hidden=hidden, retries=retries,
                      commands=commands, error_callback=error_callback,
                      convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_float(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
              minimum: float | None = ..., maximum: float | None = ..., *,
              prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
              default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
              commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
              convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> float: ...
@overload
def get_float(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
              minimum: float | None = ..., maximum: float | None = ..., *,
              prompt: str = ..., required: Literal[False], default: Any = ...,
              default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
              commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
              convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> float | None: ...
def get_float(cleaners: CleanerArg = None, validators: GetInputValidatorArg = None, minimum: float | None = None,
              maximum: float | None = None, *,
              prompt: str = 'Enter an real (floating point) number',
              required: bool = True,
              default: Any = None,
              default_str: str | None = None,
              hidden: bool = False,
              retries: int | None = None,
              commands: CommandsArg = None,
              error_callback: ErrorCallback = print_error,
              convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
              validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> float | None:
    """
    Get a real (floating point) number from the user.

    Typical use::

        ci.get_float(prompt="How tall are you, in metres?")

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param minimum: minimum value allowed. Use None (default) for no minimum value.
    :param maximum: maximum value allowed. Use None (default) for no maximum value.
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated float value

    :raises TypeError: if given an option this function does not have

    Convenience function to get a float value. Every parameter from ``prompt`` onwards is a
    keyword-only :class:`GetInput` option; most calls use one or two.
    """
    val_list = _add_range_validator(validators, minimum, maximum)
    result = GetInput(cleaners, FloatConvertor(), val_list, prompt=prompt, required=required,
                      default=default, default_str=default_str, hidden=hidden, retries=retries,
                      commands=commands, error_callback=error_callback,
                      convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_boolean(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ..., *,
                prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
                default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
                commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
                convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> bool: ...
@overload
def get_boolean(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ..., *,
                prompt: str = ..., required: Literal[False], default: Any = ...,
                default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
                commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
                convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> bool | None: ...
def get_boolean(cleaners: CleanerArg = (StripCleaner()), validators: GetInputValidatorArg = None, *,
                prompt: str = 'Enter true or false',
                required: bool = True,
                default: Any = None,
                default_str: str | None = None,
                hidden: bool = False,
                retries: int | None = None,
                commands: CommandsArg = None,
                error_callback: ErrorCallback = print_error,
                convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
                validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> bool | None:
    """
    Get a **True**/**False** value from the user.

    Typical use::

        ci.get_boolean(prompt="Enable logging?", default="False")

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated boolean value

    :raises TypeError: if given an option this function does not have

    Convenience function to get a Boolean value. See :class:`BooleanConvertor` for a list of values accepted
    for `True` and `False`. Every parameter from ``prompt`` onwards is a keyword-only :class:`GetInput`
    option; most calls use one or two.
    """
    result = GetInput(cleaners, BooleanConvertor(), validators, prompt=prompt, required=required,
                      default=default, default_str=default_str, hidden=hidden, retries=retries,
                      commands=commands, error_callback=error_callback,
                      convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_date(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
             minimum: datetime | None = ..., maximum: datetime | None = ..., *,
             prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
             default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
             commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
             convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> datetime: ...
@overload
def get_date(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ...,
             minimum: datetime | None = ..., maximum: datetime | None = ..., *,
             prompt: str = ..., required: Literal[False], default: Any = ...,
             default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
             commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
             convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> datetime | None: ...
def get_date(cleaners: CleanerArg = (StripCleaner()), validators: GetInputValidatorArg = None,
             minimum: datetime | None = None, maximum: datetime | None = None, *,
             prompt: str = 'Enter a date',
             required: bool = True,
             default: Any = None,
             default_str: str | None = None,
             hidden: bool = False,
             retries: int | None = None,
             commands: CommandsArg = None,
             error_callback: ErrorCallback = print_error,
             convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
             validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> datetime | None:
    """
    Get a date (or a time) from the user.

    Typical use::

        ci.get_date(prompt="When is the meeting?", default="today")

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param minimum: earliest date allowed. Use None (default) for no minimum value.
    :param maximum: latest date allowed. Use None (default) for no maximum value.
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated date value

    :raises TypeError: if given an option this function does not have

    Convenience function to get a date value. See :class:`DateConvertor` for more information on converting dates. Get_date
    can be used to get both times and dates. Every parameter from ``prompt`` onwards is a keyword-only
    :class:`GetInput` option; most calls use one or two.
    """
    val_list = _add_range_validator(validators, minimum, maximum)
    result = GetInput(cleaners, DateConvertor(), val_list, prompt=prompt, required=required,
                      default=default, default_str=default_str, hidden=hidden, retries=retries,
                      commands=commands, error_callback=error_callback,
                      convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_yes_no(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ..., *,
               prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
               default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
               commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
               convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> str: ...
@overload
def get_yes_no(cleaners: CleanerArg = ..., validators: GetInputValidatorArg = ..., *,
               prompt: str = ..., required: Literal[False], default: Any = ...,
               default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
               commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
               convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> str | None: ...
def get_yes_no(cleaners: CleanerArg = (StripCleaner()), validators: GetInputValidatorArg = None, *,
               prompt: str = 'Enter yes or no',
               required: bool = True,
               default: Any = None,
               default_str: str | None = None,
               hidden: bool = False,
               retries: int | None = None,
               commands: CommandsArg = None,
               error_callback: ErrorCallback = print_error,
               convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
               validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> str | None:
    """
    Get a yes/no answer from the user.

    Typical use::

        ci.get_yes_no(prompt="Are you sure?", default="no")

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated yes/no value

    :raises TypeError: if given an option this function does not have

    Convenience function to get an yes/no value. See :class:`YesNoConvertor` for a list of values accepted
    for `yes` and `no`. Every parameter from ``prompt`` onwards is a keyword-only :class:`GetInput`
    option; most calls use one or two.
    """
    result = GetInput(cleaners, YesNoConvertor(), validators, prompt=prompt, required=required,
                      default=default, default_str=default_str, hidden=hidden, retries=retries,
                      commands=commands, error_callback=error_callback,
                      convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_money(symbol: str = ..., separator: str = ..., cleaners: CleanerArg = ...,
              validators: GetInputValidatorArg = ..., precision: int | None = ...,
              rounding: str = ..., *,
              prompt: str = ..., required: Literal[True] = ..., default: Any = ...,
              default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
              commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
              convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> Decimal: ...
@overload
def get_money(symbol: str = ..., separator: str = ..., cleaners: CleanerArg = ...,
              validators: GetInputValidatorArg = ..., precision: int | None = ...,
              rounding: str = ..., *,
              prompt: str = ..., required: Literal[False], default: Any = ...,
              default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
              commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
              convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> Decimal | None: ...
def get_money(symbol: str = "$", separator: str = ",", cleaners: CleanerArg = (StripCleaner(),),
              validators: GetInputValidatorArg = None, precision: int | None = None,
              rounding: str = "ROUND_HALF_UP", *,
              prompt: str = 'Enter an amount of money',
              required: bool = True,
              default: Any = None,
              default_str: str | None = None,
              hidden: bool = False,
              retries: int | None = None,
              commands: CommandsArg = None,
              error_callback: ErrorCallback = print_error,
              convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
              validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> Decimal | None:
    """
    Get an amount of money from the user.

    Typical use::

        ci.get_money(prompt="How much did it cost?", precision=2)

    :param symbol: Symbol for the currency used (default: "$").
    :param separator: Thousands separator (default: ",").
    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param precision: digits after the decimal point to round the amount to. ``precision=2`` gives
        whole cents. **None** (the default) does not round at all.
    :param rounding: the rounding rule to use, see :class:`DecimalConvertor`.
    :param prompt: the string to use for the prompt
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: a Decimal value for the cleaned, converted currency value entered.

    :raises TypeError: if given an option this function does not have

    Convenience function for getting values for money. See :class:`DecimalConvertor` for a list of values accepted
    for `rounding`. The currency symbol is stripped off and the `Decimal` value returned.

    ``precision`` and ``rounding`` are this function's own parameters, not :class:`GetInput` options.
    They used to arrive through the ``**options`` bag, which passed them on to :class:`GetInput` as
    well -- so the documented way to ask for whole cents logged two spurious "unknown option"
    warnings on every call.
    """
    if symbol == "$":
        pattern = r"^\$"
    else:
        pattern = "^" + symbol

    symbol_cleaner = RegexCleaner(pattern, '', 1)
    thousands_cleaner = RemoveCleaner(separator)
    # Fixing: this was `list(cleaners)`, so get_money was the one get_* function that
    # could not take a single cleaner -- get_money(cleaners=StripCleaner()) raised
    # "'StripCleaner' object is not iterable" while every sibling accepted it, since
    # they hand cleaners straight to compose, which copes with either. put_in_a_list
    # is the helper the package already has for exactly this.
    new_cleaners = put_in_a_list(cleaners) + [symbol_cleaner, thousands_cleaner]

    convertor = DecimalConvertor(precision=precision, rounding=rounding)
    result = GetInput(new_cleaners, convertor, validators, prompt=prompt, required=required,
                      default=default, default_str=default_str, hidden=hidden, retries=retries,
                      commands=commands, error_callback=error_callback,
                      convertor_error_fmt=convertor_error_fmt,
                      validator_error_fmt=validator_error_fmt).get_input()
    return result


@overload
def get_list(elem_get_input: GetInput | None = ..., cleaners: CleanerArg = ...,
             validators: GetInputValidatorArg = ..., value_error_str: str = ...,
             delimiter: str = ..., *,
             prompt: str | None = ..., required: Literal[True] = ..., default: Any = ...,
             default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
             commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
             convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> list[Any]: ...
@overload
def get_list(elem_get_input: GetInput | None = ..., cleaners: CleanerArg = ...,
             validators: GetInputValidatorArg = ..., value_error_str: str = ...,
             delimiter: str = ..., *,
             prompt: str | None = ..., required: Literal[False], default: Any = ...,
             default_str: str | None = ..., hidden: bool = ..., retries: int | None = ...,
             commands: CommandsArg = ..., error_callback: ErrorCallback = ...,
             convertor_error_fmt: str = ..., validator_error_fmt: str = ...) -> list[Any] | None: ...
def get_list(elem_get_input: GetInput | None = None, cleaners: CleanerArg = None,
             validators: GetInputValidatorArg = None, value_error_str: str = 'list of values',
             delimiter: str = ',', *,
             prompt: str | None = None,
             required: bool = True,
             default: Any = None,
             default_str: str | None = None,
             hidden: bool = False,
             retries: int | None = None,
             commands: CommandsArg = None,
             error_callback: ErrorCallback = print_error,
             convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
             validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> list[Any] | None:
    """
    Get a list of values from the user.

    Typical use::

        ci.get_list(prompt="Which colors do you like?")

    :param elem_get_input: an instance of a :class:`GetInput` to apply to each element
    :param cleaners: cleaners to be applied to the input line before the :class:`ListConvertor` is applied.
    :param validators: list of `validators <validators.html>`_ to apply to validate the converted list
    :param value_error_str: the error string for improper value inputs
    :param delimiter: the delimiter to use between values
    :param prompt: the string to use for the prompt. Defaults to one naming ``delimiter``.
    :param required: **False** to accept a blank response. See :class:`GetInput`.
    :param default: the value to use for a blank response. An iterable is joined with ``delimiter``
        for display, so a list default shows the way the user would have typed it.
    :param default_str: the string to display for the default value
    :param hidden: **True** to keep the typed input off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: dictionary of commands callable from the prompt
    :param error_callback: called when a value is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the cleaned, converted, validated list of values. For more information on the `value_error_str`,
      `delimeter`, `elem_convertor`, and elem_valudator` parameters see :class:`ListConvertor`.

    :raises TypeError: if given an option this function does not have

    Get a homogenous list of values. The :meth:`GetInput.process_value` method on the ``elem_get_input`` :class:`GetInput`
    instance is called for each element in the list.

    Example usage - get a list of integers between 3 and 5 numbers long, separated by colons (:)::

        elem_gi = GetInput(convertor=IntConvertor())
        length_validator = RangeValidator(min_val=3, max_val=5)
        list_validator = ListValidator(len_validator=length_validator)
        prompt_str = 'Enter a list of integers, each between 3 and 5, separated by ":"'
        result = get_list(prompt=prompt_str, elem_get_input=elem_gi, validators=list_validator, delimiter=":")

    """
    # The default prompt names the delimiter, so it cannot be a constant in the signature the way
    # the other get_* functions' prompts are.
    use_prompt = 'Enter a list of values (separated by "{}")'.format(delimiter) if prompt is None else prompt

    if default is None or isstring(default):
        default_val = default
    # Fixing: was `collections.Iterable`, removed from the collections
    # namespace in Python 3.10, so a non-string iterable default raised
    # AttributeError on every supported version. input_utils.py already
    # uses collections.abc for exactly this reason.
    elif isinstance(default, collections.abc.Iterable):
        default_val = (delimiter + ' ').join(default)
    else:
        default_val = str(default)

    convertor = ListConvertor(value_error_str=value_error_str, delimiter=delimiter, elem_get_input=elem_get_input)
    gi = GetInput(cleaners, convertor, validators, prompt=use_prompt, required=required,
                  default=default_val, default_str=default_str, hidden=hidden, retries=retries,
                  commands=commands, error_callback=error_callback,
                  convertor_error_fmt=convertor_error_fmt, validator_error_fmt=validator_error_fmt)

    result = gi.get_input()
    return result
