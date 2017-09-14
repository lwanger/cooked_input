"""
This file contains convertors classes for cooked_input

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import dateparser
import csv
from io import StringIO
from future.utils import raise_from

from .input_utils import put_in_a_list
from .error_callbacks import ConvertorError


TABLE_ID = 0
TABLE_VALUE = 1
TABLE_ID_OR_VALUE = -1


###
### Convertors:
###
# class Convertor(metaclass=ABCMeta):
class Convertor(object):
    # Abstract base class for conversion classes
    def __init__(self, value_error_str, **kwargs):
        self.value_error_str = value_error_str

    # @abstractmethod
    def __call__(self, value, error_callback, convertor_fmt_str):
        pass


class IntConvertor(Convertor):
    """
    convert the cleaned input to an integer.

    :param base:  the radix base to use for the int conversion (default=10). Legal values are 0 and 2-36. See
        the Python int function for more information.
    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, base=10, value_error_str='an integer number', **kwargs):

        self._base = base
        super(IntConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        result = None
        try:
            result = int(value, self._base)
        except (ValueError) as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise_from(ConvertorError(str(ve)), ve)

        return result

    def __repr__(self):
        return 'IntConvertor(base=%d, value_error_str=%s)' % (self._base, self.value_error_str)


class FloatConvertor(Convertor):
    """
    convert to a floating point number

    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='a float number', **kwargs):
        super(FloatConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        result = None

        try:
            result = float(value)
        except ValueError as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise_from(ConvertorError(str(ve)), ve)

        return result

    def __repr__(self):
        return 'FloatConvertor(%s)' % self.value_error_str


class BooleanConvertor(Convertor):
    """
    convert to a boolean value (True or False).

    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='true or false', **kwargs):
        super(BooleanConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        true_set = {'t', 'true', 'y', 'yes', '1'}
        false_set = {'f', 'false', 'n', 'no', '0'}

        if value.lower() in true_set:
            return True
        elif value.lower() in false_set:
            return False
        else:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError('value not true or false.')

    def __repr__(self):
        return 'BooleanConvertor(%s)' % self.value_error_str


class ListConvertor(Convertor):
    """
    convert to a list.

    :param value_error_str: the error string to use when an improper value is input.
    :param delimiter: the single character delimiter to use for parsing the list. If None, will sniff the value
        (ala CSV library.)
    :param elem_convertor: the convertor function to use for each element of the list (e.g. IntConvertor converts each
        element of the list to an integer.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='list of values', delimiter=',', elem_convertor=None, **kwargs):
        self.delimeter = delimiter
        self.elem_convertor = elem_convertor
        super(ListConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        buffer = StringIO(value)

        if self.delimeter is None:
            dialect = csv.Sniffer().sniff(value)
            dialect.skipinitialspace = True
        else:
            csv.register_dialect('my_dialect', delimiter=self.delimeter, quoting=csv.QUOTE_MINIMAL, skipinitialspace=True)
            dialect = csv.get_dialect('my_dialect')

        reader = csv.reader(buffer, dialect)
        lst = next(reader)

        try:
            if self.elem_convertor:
                converted_list = [self.elem_convertor(item, error_callback, convertor_fmt_str) for item in lst]
            else:
                converted_list = lst
        except ConvertorError:
            raise ConvertorError(self.elem_convertor.value_error_str)

        return converted_list

    def __repr__(self):
        return 'ListConvertor(%s)' % self.value_error_str


class DateConvertor(Convertor):
    """
    convert to a datetime. Converts the cleaned input to an datetime value. Dateparser is used for the parsing, allowing
    a lot of flexibility in how date input is entered (e.g. '12/12/12', 'October 1, 2015', 'today', or 'next Tuesday').
    For more information about dateparser see: https://dateparser.readthedocs.io/en/latest/

    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='a date', **kwargs):
        super(DateConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        result = dateparser.parse(value)
        if result:
            return result
        else:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError('value not a valid date')

    def __repr__(self):
        return 'DateConvertor(%s)' % self.value_error_str


class YesNoConvertor(Convertor):
    """
    convert to 'yes' or 'no'.

    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='yes or no', **kwargs):
        super(YesNoConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        yes_set = {'y', 'yes', 'yeah', 'yup', 'aye', 'qui', 'si', 'ja', 'ken', 'hai', 'gee', 'da', 'tak', 'affirmative'}
        no_set = {'n', 'no', 'nope', 'na', 'nae', 'non', 'negatory', 'nein', 'nie', 'nyet', 'lo'}

        if value.lower() in yes_set:
            return 'yes'
        elif value.lower() in no_set:
            return 'no'
        else:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError('value not yes or no.')

    def __repr__(self):
        return 'YesNoConvertor(%s)' % self.value_error_str


class TableConvertor(Convertor):
    """
    convert to the id or value in the supplied table.

    kwargs values:
        value_error_str: the error string to use if the value cannot be converted

        input_value: TABLE_VALUE, if a value from the table should be expected, TABLE_ID if an id is expected. TABLE_ID_OR_VALUE if the user can enter either.

    :param table: the table of values. Table is a list of  tuples for each row. The tuples are (id, value) pairs.
    :param convertor: the convertor to apply to the value entered
    :param kwargs: see above
    """
    def __init__(self, table, convertor=None, **kwargs):
        """
        Convert to the id or value in a table

        kwargs values:
            value_error_str: the error string to use if the value cannot be converted
            input_value: TABLE_VALUE, if a value from the table should be expected, TABLE_ID if an id is expected.
                TABLE_ID_OR_VALUE if can enter either

        :param table: the table of values. Table is a list of  tuples for each row. The tuples are (id, value) pairs.
        :param convertor: the convertor to apply to the value entered
        :param kwargs: see above
        """
        self._table = table
        self._convertor = convertor
        self._input_value = TABLE_VALUE
        self.value_error_str = None

        for k, v in kwargs.items():
            if k == 'value_error':
                self.value_error_str = v
            elif k == 'input_value':
                if v in (TABLE_ID, TABLE_VALUE, TABLE_ID_OR_VALUE):
                    self._input_value = v

        if self.value_error_str is None:
            if self._input_value == TABLE_ID_OR_VALUE:
                self.value_error_str = 'an id or value from the table'
            elif self._input_value == TABLE_ID:
                self.value_error_str = 'an id from the table'
            else:
                self.value_error_str = 'a value from the table'
        else:
            self.value_error_str = self.value_error_str

        super_options_to_skip = {'value_error', 'input_value'}
        super_kwargs = {k: v for k, v in kwargs.items() if k not in super_options_to_skip}
        super(TableConvertor, self).__init__(self.value_error_str, **super_kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        if self._convertor:
            result = self._convertor(value, error_callback, convertor_fmt_str)
        else:
            result = value

        if self._input_value == TABLE_VALUE:
            if result is not None and result in (item[1] for item in self._table):
                return result
            else:
                error_callback(convertor_fmt_str, value, 'a valid table value')
                raise ConvertorError('%s not a valid table value' % value)
        elif self._input_value == TABLE_ID:
            try:
                result = int(value)
            except ValueError:
                result = None

            if result is None or result not in (item[0] for item in self._table):
                error_callback(convertor_fmt_str, value, 'a valid table id')
                raise ConvertorError('%s not a valid table id' % value)
        else:  # input_value == TABLE_ID_OR_VALUE
            try:
                if result in (item[1] for item in self._table):
                    result = value
                elif int(result) in (item[0] for item in self._table):
                    result = int(result)
                else:
                    result = None
            except ValueError:
                result = None

            if result is None:
                error_callback(convertor_fmt_str, value, 'a valid table id')
                raise ConvertorError('%s not a valid table id' % value)

        return result

    def __repr__(self):
        return 'TableConvertor(%s)' % self.value_error_str


    """
    convert the cleaned input to the integer row of a table
    """
class ChoiceIndexConvertor(Convertor):
    """
    convert a value from an ordered list of choice to the integer index of the value in the list This is useful to get
    the row index from a table of values.

    :param values:  an ordered list of values
    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, values=(), value_error_str='a valid row number', **kwargs):
        choices_list = put_in_a_list(values)
        self._choices = {v: i for i,v in enumerate(choices_list)}
        super(ChoiceIndexConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        result = None
        try:
            result = self._choices[value]
        except (KeyError) as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise_from(ConvertorError(str(ve)), ve)

        return result

    def __repr__(self):
        return 'ChoiceIndexConvertor(choices={}, value_error_str={})'.format(self._choices, self.value_error_str)