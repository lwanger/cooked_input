"""
This file contains convertors classes for cooked_input

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""

from __future__ import annotations

import csv
import dateparser
import decimal
from datetime import datetime
from io import StringIO
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any


from ._typing import ErrorCallback
from .error_callbacks import ConvertorError

if TYPE_CHECKING:
    # get_input imports this module, so the reverse import only exists for annotations.
    from .get_input import GetInput


TABLE_ID = 0
TABLE_VALUE = 1
TABLE_ID_OR_VALUE = -1


###
### Convertors:
###
class Convertor(metaclass=ABCMeta):
    """
    Abstract base class for convertors. Subclasses must implement :meth:`__call__`, which takes
    the cleaned value and returns it converted to the target type.

    Fixing: this used to say ``__metaclass__ = ABCMeta``, the Python 2 spelling, which on
    Python 3 is an inert class attribute. Nothing was enforced -- ``Convertor('')``
    instantiated happily and a subclass that forgot ``__call__`` returned **None** from every
    conversion instead of failing.
    """
    def __init__(self, value_error_str: str) -> None:
        self.value_error_str = value_error_str

    @abstractmethod
    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> Any:
        # Any is the honest return type for the base: the whole point of a convertor is
        # to decide what the text becomes, and the concrete subclasses below say
        # precisely which type each of them produces.
        pass


class IntConvertor(Convertor):
    """
    convert the cleaned input to an integer.

    :param int base:  the radix base to use for the int conversion (default=10)
    :param str value_error_str: (optional) the error string to use when an improper value is input

    :return: ``value`` converted to `int`
    :rtype: int
    :raises ConvertorError: if ``value`` cannot be converted to `int`


    Legal values for the `base` parameter are 0 and 2-36. See the Python `int <https://docs.python.org/3/library/functions.html#int>`_
    built-in function for more information.
    """
    def __init__(self, base: int = 10, value_error_str: str = 'an integer number') -> None:
        self._base = base
        super(IntConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> int:
        try:
            return int(value, self._base)
        except (ValueError) as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError(str(ve)) from ve

    def __repr__(self) -> str:
        return 'IntConvertor(base=%d, value_error_str=%s)' % (self._base, self.value_error_str)


class FloatConvertor(Convertor):
    """
    convert to a floating point number.

    :param str value_error_str: (optional) the error string to use when an improper value is input

    :return: ``value`` converted to `float`
    :rtype: float
    :raises ConvertorError: if ``value`` cannot be converted to `float`
    """
    def __init__(self, value_error_str: str = 'a float number') -> None:
        super(FloatConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> float:
        try:
            return float(value)
        except ValueError as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError(str(ve)) from ve

    def __repr__(self) -> str:
        return 'FloatConvertor(%s)' % self.value_error_str


class BooleanConvertor(Convertor):
    """
    convert to a boolean value (**True** or **False**.)

    :param str value_error_str: (optional) the error string to use when an improper value is input

    :return: ``value`` converted to a `boolean`
    :rtype: boolean (**True** or **False**)
    :raises ConvertorError: if ``value`` cannot be converted to `bool`


    `BooleanConvertor` returns **True** for input values: 't', 'true', 'y', 'yes', and '1'. `BooleanConvertor` returns
    **False** for input values: 'f', 'false', 'n', 'no', '0'.
    """
    def __init__(self, value_error_str: str = 'true or false') -> None:
        super(BooleanConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> bool:
        true_set = {'t', 'true', 'y', 'yes', '1'}
        false_set = {'f', 'false', 'n', 'no', '0'}

        if value.lower() in true_set:
            return True
        elif value.lower() in false_set:
            return False
        else:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError('value not true or false.')

    def __repr__(self) -> str:
        return 'BooleanConvertor(%s)' % self.value_error_str


class ListConvertor(Convertor):
    """
    convert to a list.

    :param GetInput elem_get_input: an instance of a :class:`GetInput` to apply to each element. If ``None`` (default)
        each element in the list is a string
    :param str delimiter: (optional) the single character delimiter to use for parsing the list. If None, will sniff the value
        (ala CSV library.)
    :param str value_error_str: (optional) the error string for improper value inputs

    :return: a `list` values, where each item in the list is of the type returned by ``elem_get_input``
    :rtype: List[Any] (element type of list determined by ``elem_get_input``)
    :raises ConvertorError: if ``elem_get_input``'s :meth:`GetInput.process_value` fails

    Converts to a homogenous list of values. The :meth:`GetInput.process_value` method on the ``elem_get_input``
    :class:`GetInput` instance is called for each element in the list.

    For example, the accept a list of integers separated by colons (':') and return it as a Python list of ints::

      prompt_str = 'Enter a list of integers (separated by ":")'
      lc = ListConvertor(delimiter=':', elem_get_input=GetInput(convertor=IntConvertor()))
      result = get_input(prompt=prompt_str, convertor=lc)
    """
    def __init__(self, elem_get_input: GetInput | None = None, delimiter: str | None = ',',
                 value_error_str: str = 'list of values') -> None:
        self._delimeter = delimiter
        self._elem_get_input = elem_get_input
        super(ListConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> list[Any]:
        buffer = StringIO(value)

        if self._delimeter is None:
            dialect = csv.Sniffer().sniff(value)
            dialect.skipinitialspace = True
        else:
            csv.register_dialect('my_dialect', delimiter=self._delimeter, quoting=csv.QUOTE_MINIMAL, skipinitialspace=True)
            dialect = csv.get_dialect('my_dialect')

        converted_list: list[Any] = []
        reader = csv.reader(buffer, dialect)

        try:
            lst = next(reader)
        except (StopIteration):
            return converted_list

        try:
            if self._elem_get_input:
                for item in lst:
                    # Not `value`: that is the whole comma-separated string this method
                    # was handed, and rebinding it to one converted element made the two
                    # different things share a name.
                    valid, converted_elem = self._elem_get_input.process_value(item)

                    if valid is True:
                        converted_list.append(converted_elem)
                    else:
                        raise ConvertorError
            else:
                converted_list = lst
        except ConvertorError:
            raise ConvertorError(self.value_error_str)

        return converted_list

    def __repr__(self) -> str:
        return 'ListConvertor(%s)' % self.value_error_str


class DateConvertor(Convertor):
    """
    convert to a `datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_ value.

    :param str value_error_str: (optional) the error string to use when an improper value is input

    :return: ``value`` converted to a `datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_
    :rtype: `datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_
    :raises ConvertorError: if dateparser is unable to convert ``value`` to a
        `datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_


    Converts the cleaned input to an datetime value. Dateparser is used for the parsing, allowing
    a lot of flexibility in how date input is entered (e.g. '12/12/12', 'October 1, 2015', 'today', or 'next Tuesday').
    For more information about dateparser see: `<https://dateparser.readthedocs.io/en/latest/>`_
    """
    def __init__(self, value_error_str: str = 'a date') -> None:
        super(DateConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> datetime:
        result = dateparser.parse(value)
        if result:
            return result
        else:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError('value not a valid date')

    def __repr__(self) -> str:
        return 'DateConvertor(%s)' % self.value_error_str


class YesNoConvertor(Convertor):
    """
    convert to 'yes' or 'no'.

    :param str value_error_str: (optional) the error string to use when an improper value is input

    :return: a string set to either **"yes"** or **"no"**
    :rtype: str (**"yes"** or **"no"**)
    :raises ConvertorError: if ``value`` cannot be converted to **"yes"** or **"no"**

    **YesNoConvertor** returns `yes` for input values: 'y', 'yes', 'yeah', 'yup', 'aye', 'qui', 'si', 'ja', 'ken',
    'hai', 'gee', 'da', 'tak', 'affirmative'. `YesNoConvertor` returns `no` for input values: 'n', 'no', 'nope',
    'na', 'nae', 'non', 'negatory', 'nein', 'nie', 'nyet', 'lo'.
    """
    def __init__(self, value_error_str: str = 'yes or no') -> None:
        super(YesNoConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> str:
        yes_set = {'y', 'yes', 'yeah', 'yup', 'aye', 'qui', 'si', 'ja', 'ken', 'hai', 'gee', 'da', 'tak', 'affirmative'}
        no_set = {'n', 'no', 'nope', 'na', 'nae', 'non', 'negatory', 'nein', 'nie', 'nyet', 'lo'}

        if value.lower() in yes_set:
            return 'yes'
        elif value.lower() in no_set:
            return 'no'
        else:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError('value not yes or no.')

    def __repr__(self) -> str:
        return 'YesNoConvertor(%s)' % self.value_error_str


class ChoiceConvertor(Convertor):
    """
    Convert a value to its mapped value in a dictionary.

    :param Dict value_dict:  a dictionary containing keys to map from and values to map to
    :param str value_error_str: (optional) the error string to use when an improper value is input

    :raises ConvertorError if ``value`` key is not found in ``value_dict``

    :return: the `value` associated with the choice in ``value_dict`` (e.g. `value_dict[value]`)
    :rtype: Any (type is dependent on mapped value in ``value_dict``)

    convert a value to it's return value in a dictionary (i.e. value_dict[value]). Can be used to map the row
    index from a table of values or to map multiple tags to a single choice.

    For example, to use a number to pick from a list of colors::

      value_map = {'1': 'red', '2': 'green', '3': 'blue'}
      choice_convertor = ci.ChoiceConvertor(value_dict=value_map)
      result = ci.get_input(convertor=choice_convertor, prompt='Pick a color (1 - red, 2 - green, 3 - blue)')
    """
    def __init__(self, value_dict: dict[Any, Any], value_error_str: str = 'a valid row number') -> None:
        self._choices = value_dict
        super(ChoiceConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback, convertor_fmt_str: str) -> Any:
        try:
            return self._choices[value]
        except (KeyError) as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError(str(ve)) from ve

    def __repr__(self) -> str:
        return 'ChoiceConvertor(choices={}, value_error_str={})'.format(self._choices, self.value_error_str)


class DecimalConvertor(Convertor):
    """
    convert the cleaned input to a Decimal value.

    :param int precision: the fixed number of digits after the decimal point. **None** (the
        default) keeps every digit entered and rounds nothing.
    :param str rounding:  rules used for rounding (default: "ROUND_HALF_UP")
    :param str value_error_str: (optional) the error string to use when an improper value is input

    :return: ``value`` converted to `Decimal`
    :rtype: Decimal
    :raises ConvertorError: if ``value`` cannot be converted to `Decimal`
    :raises ValueError: at construction, if ``rounding`` is not one of the legal names or
        ``precision`` is not a whole number

    Converts the value to a Decimal value (see the Python standard library Decimal module for me details.)

    ``precision`` counts digits after the decimal point, not significant digits, so
    ``DecimalConvertor(precision=2)('1234.567')`` gives ``Decimal('1234.57')``. This is what makes
    :func:`get_money` useful: ``get_money(precision=2)`` returns an amount in whole cents. A
    negative ``precision`` rounds to the left of the decimal point -- ``precision=-2`` rounds to
    hundreds.

    The rounding parameter sets the rules for rounding the value, and only has an effect when
    ``precision`` is set. The default rounding rule is "ROUND_HALF_UP". Legal
    values for the `rounding` parameter are: "ROUND_CEILING", "ROUND_DOWN", "ROUND_FLOOR", "ROUND_HALF_DOWN",
    "ROUND_HALF_EVEN", "ROUND_HALF_UP", "ROUND_UP", and "ROUND_05UP".

    See the Python `Decimal <https://docs.python.org/3/library/decimal.html>`_
    """
    def _rounding_str_to_int(self, rounding_str: str) -> str:
        # Despite the name this maps each name to itself: decimal's rounding constants
        # are strings (decimal.ROUND_UP == 'ROUND_UP'), so the dict's real job is to
        # reject anything that is not one of the eight legal names.
        rounding_dict = {
            "ROUND_CEILING": decimal.ROUND_CEILING,
            "ROUND_DOWN": decimal.ROUND_DOWN,
            "ROUND_FLOOR": decimal.ROUND_FLOOR,
            "ROUND_HALF_DOWN": decimal.ROUND_HALF_DOWN,
            "ROUND_HALF_EVEN": decimal.ROUND_HALF_EVEN,
            "ROUND_HALF_UP": decimal.ROUND_HALF_UP,
            "ROUND_UP": decimal.ROUND_UP,
            "ROUND_05UP": decimal.ROUND_05UP,
        }

        try:
            return rounding_dict[rounding_str]
        except KeyError as ke:
            # Fixing: this used to escape as a bare KeyError showing only the bad name,
            # leaving the caller to go and find the legal ones for themselves.
            raise ValueError('DecimalConvertor: unknown rounding {!r} -- legal values are: {}'.format(
                rounding_str, ', '.join(sorted(rounding_dict)))) from ke

    def _rounding_int_to_str(self, rounding_int: str) -> str:
        rounding_dict = {
            decimal.ROUND_CEILING: "ROUND_CEILING",
            decimal.ROUND_DOWN: "ROUND_DOWN",
            decimal.ROUND_FLOOR: "ROUND_FLOOR",
            decimal.ROUND_HALF_DOWN: "ROUND_HALF_DOWN",
            decimal.ROUND_HALF_EVEN: "ROUND_HALF_EVEN",
            decimal.ROUND_HALF_UP: "ROUND_HALF_UP",
            decimal.ROUND_UP: "ROUND_UP",
            decimal.ROUND_05UP: "ROUND_05UP"
        }
        return rounding_dict[rounding_int]

    def __init__(self, precision: int | None = None, rounding: str = "ROUND_HALF_UP",
                 value_error_str: str = 'a decimal number') -> None:
        if precision is not None and not isinstance(precision, int):
            raise ValueError('DecimalConvertor: precision must be a whole number of decimal '
                             'places or None -- got {!r}'.format(precision))

        self._precision = precision
        self._rounding = self._rounding_str_to_int(rounding)

        # Fixing: the precision used to be the prec of this context, which counts
        # significant digits rather than the digits after the decimal point the docstring
        # promises. Quantizing to an exponent is what gives decimal places, and it needs a
        # precision large enough not to clip the result it is asked to produce.
        self._context = decimal.Context(prec=decimal.MAX_PREC, rounding=self._rounding)
        super(DecimalConvertor, self).__init__(value_error_str)

    def __call__(self, value: str, error_callback: ErrorCallback,
                 convertor_fmt_str: str) -> decimal.Decimal:
        try:
            converted = decimal.Decimal(value)

            if self._precision is not None:
                # Fixing: this used to be `decimal.Decimal(value, self._context)`. Passing
                # a context to the Decimal constructor only affects error signalling -- it
                # applies neither prec nor rounding -- so both settings were silently
                # inert and DecimalConvertor(precision=2, rounding='ROUND_DOWN')('1.999')
                # returned 1.999 unchanged.
                converted = self._context.quantize(converted, decimal.Decimal(1).scaleb(-self._precision))

            return converted
        except (ValueError, decimal.InvalidOperation) as ve:
            # Fixing: decimal raises InvalidOperation, an ArithmeticError, for a value it
            # cannot parse, so the ValueError-only handler never fired -- bad input escaped
            # as InvalidOperation and error_callback was never called. A non-string value
            # still raises TypeError, as it does in IntConvertor and FloatConvertor.
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError(str(ve)) from ve

    def __repr__(self) -> str:
        rounding_str = self._rounding_int_to_str(self._rounding)
        return 'DecimalConvertor(precision=%s, rounding=%s, value_error_str=%s)' % (self._precision, rounding_str, self.value_error_str)
