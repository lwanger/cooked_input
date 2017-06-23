"""
get_input module to get values from the command line.

convertor classes

This file contains convertors classes for io_get_input


Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
import dateparser


TABLE_ID = 0
TABLE_VALUE = 1
TABLE_ID_OR_VALUE = -1


####
#### Convertors:
####
# class Convertor(metaclass=ABCMeta):
class Convertor(object):
    # Abstract base class for conversion classes
    def __init__(self, value_error_str):
        self.value_error_str = value_error_str

    # @abstractmethod
    def __call__(self, value):
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
        self.value_error_str = value_error_str
        if sys.version_info[0] > 2:
            super().__init__(value_error_str)
        else:
            super(IntConvertor, self).__init__(self.value_error_str)

    def __call__(self, value):
        result = int(value, self._base)
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
        self.value_error_str = value_error_str
        if sys.version_info[0] > 2:
            super().__init__(value_error_str)
        else:
            super(FloatConvertor, self).__init__(self.value_error_str)

    def __call__(self, value):
        result = float(value)
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
        self.value_error_str = value_error_str
        if sys.version_info[0] > 2:
            super().__init__(value_error_str)
        else:
            super(BooleanConvertor, self).__init__(self.value_error_str)

    def __call__(self, value):
        true_set = {'t', 'true', 'y', 'yes', '1'}
        false_set = {'f', 'false', 'n', 'no', '0'}

        if value.lower() in true_set:
            return True
        elif value.lower() in false_set:
            return False
        else:
            raise ValueError('value not true or false.')

    def __repr__(self):
        return 'BooleanConvertor(%s)' % self.value_error_str


class DateConvertor(Convertor):
    """
    convert to a datetime. Converts the cleaned input to an datetime value. Dateparser is used for the parsing, allowing
    a lot of flexibility in how date input is entered (e.g. '12/12/12', 'October 1, 2015', 'today', or 'next Tuesday').
    For more information about dateparser see: https://dateparser.readthedocs.io/en/latest/

    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='a date', **kwargs):
        self.value_error_str = value_error_str
        if sys.version_info[0] > 2:
            super().__init__(value_error_str)
        else:
            super(DateConvertor, self).__init__(self.value_error_str)

    def __call__(self, value):
        result = dateparser.parse(value)
        if result:
            return result
        else:
            raise ValueError('value not a valid date')

    def __repr__(self):
        return 'DateConvertor(%s)' % self.value_error_str


class YesNoConvertor(Convertor):
    """
    convert to 'yes' or 'no'.

    :param value_error_str: the error string to use when an improper value is input.
    :param kwargs: no kwargs are currently supported.
    """
    def __init__(self, value_error_str='yes or no', **kwargs):
        self.value_error_str = value_error_str
        if sys.version_info[0] > 2:
            super().__init__(value_error_str)
        else:
            super(YesNoConvertor, self).__init__(self.value_error_str)

    def __call__(self, value):
        yes_set = {'y', 'yes', 'yeah', 'yup', 'aye', 'qui', 'si', 'ja', 'ken', 'hai', 'gee', 'da', 'tak', 'affirmative' }
        no_set = {'n', 'no', 'nope', 'na', 'nae', 'non', 'negatory', 'nein', 'nie', 'nyet', 'lo'}

        if value.lower() in yes_set:
            return 'yes'
        elif value.lower() in no_set:
            return 'no'
        else:
            raise ValueError('value not yes or no.')

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
            # self.value_error_str = 'a value from the table' if self._input_value else 'an id from the table'
            if self._input_value == TABLE_ID_OR_VALUE:
                self.value_error_str = 'an id or value from the table'
            elif self._input_value == TABLE_ID:
                self.value_error_str = 'an id from the table'
            else:
                self.value_error_str = 'a value from the table'
        else:
            self.value_error_str = self.value_error_str

        if sys.version_info[0] > 2:
            super().__init__(self.value_error_str)
        else:
            super(TableConvertor, self).__init__(self.value_error_str)

    def __call__(self, value):
        if self._convertor:
            result = self._convertor(value)
        else:
            result = value

        if self._input_value == TABLE_VALUE:
            if result is not None and result in (item[1] for item in self._table):
                return result
            else:
                raise ValueError('%s not a valid table value' % value)
        elif self._input_value == TABLE_ID:
            result = int(value)
            if result is None or result not in (item[0] for item in self._table):
                raise ValueError('%s not a valid table id' % value)
        else: # input_value == TABLE_ID_OR_VALUE
            if result in (item[1] for item in self._table):
                result = value
            elif int(result) in (item[0] for item in self._table):
                return int(result)
            else:
                raise ValueError('%s not a valid table id' % value)

        return result

    def __repr__(self):
        return 'DateConvertor(%s)' % self.value_error_str