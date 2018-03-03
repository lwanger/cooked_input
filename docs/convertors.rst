Convertors
**********

.. module::  convertors

Convertors classes for converting the string input to the desired output type. The `GetInput <get_input.html>`_ class
calls the Convertor after cleaning and before validation.


Creating Convertors
===================

Convertor classes inherit from the Convertor base class. They must be callable, with the `__call__` dunder
method taking three parameters: the value to convert, a function to call when an error occurs and the format string
for the error function. The `__call__` method returns the converted value. Error conditions are handled by calling
the `error_callback` function . See `error_callbacks <error_callbacks.html>`_ for more information on error functions
and their format strings. The `__init__` method should use `super` to call the `__init__` method on the Convertor base
class so `value_error_str` gets set.

An example of a convertor to change the input value to an integer looks like::

    class IntConvertor(Convertor):
        # convert to a value to an integer
        def __init__(self, base=10, value_error_str='an integer number'):
            self._base = base
            super(IntConvertor, self).__init__(value_error_str)

        def __call__(self, value, error_callback, convertor_fmt_str):
            try:
                return int(value, self._base)
            except ValueError:
                error_callback(convertor_fmt_str, value, 'an int')
                raise   # re-raise the exception

        def __repr__(self):
            return 'IntConvertor(base={}, value_error_str={})'.format(self._base, self.value_error_str)

Convertors
==========

BooleanConvertor
----------------

.. autoclass:: cooked_input.BooleanConvertor


DateConvertor
-------------

.. autoclass:: cooked_input.DateConvertor


FloatConvertor
--------------

.. autoclass:: cooked_input.FloatConvertor


IntConvertor
------------

.. autoclass:: cooked_input.IntConvertor


ListConvertor
-------------

.. autoclass:: cooked_input.ListConvertor


YesNoConvertor
--------------

.. autoclass:: cooked_input.YesNoConvertor

ChoiceConvertor
---------------

.. autoclass:: cooked_input.ChoiceConvertor
