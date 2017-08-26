Convertors
**********

.. module::  convertors

Convertors classes for converting the string input to the desired output. Conversion is done after cleaning and before
validation.


Creating Convertors
===================

Convertor classes inherit from the Convertor metaclass. They must be callable, with the __call__ dunder
method taking three parameters: the value to convert, a function to call when an error occurs and the format string
for the error function. See the [error_callbacks] for more information on error functions and their format strings.

An example of a convertor to change the input value to an integer looks like::

    class IntConvertor(Convertor):
        # convert to a lower case number
        def __init__(self, base=10, value_error_str='an integer number', **kwargs):
            self._base = base
            self.value_error_str = value_error_str
            super(IntConvertor, self).__init__(self.value_error_str)

        def __call__(self, value, error_callback, convertor_fmt_str):
            result = int(value, self._base)

            try:
                result = int(value, self._base)
            except ValueError:
                error_callback(convertor_fmt_str, value, 'an int')
                raise   # re-raise the exception

            return result

        def __repr__(self):
            return 'IntConvertor(base=%d, value_error_str=%s)' % (self._base, self.value_error_str)

Convertors
==========

IntConvertor
------------

.. autoclass:: cooked_input.IntConvertor

FloatConvertor
--------------

.. autoclass:: cooked_input.FloatConvertor

BooleanConvertor
----------------

.. autoclass:: cooked_input.BooleanConvertor

ListConvertor
-------------

.. autoclass:: cooked_input.ListConvertor

DateConvertor
-------------

.. autoclass:: cooked_input.DateConvertor

YesNoConvertor
--------------

.. autoclass:: cooked_input.YesNoConvertor

TableConvertor
--------------

.. autoclass:: cooked_input.TableConvertor


