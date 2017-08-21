Convertors
==========

.. module::  convertors

Convertors classes for converting the string input to the desired output. Conversion is done after cleaning and before
validation.


Creating Convertors
-------------------

Convertor classes inherit from the Convertor metaclass. They must be callable, with the __call__ dunder
method taking one parameter, the value. An example of a convertor to change the input value to an integer
looks like::

    class IntConvertor(Convertor):
        # convert to a lower case number
        def __init__(self, base=10, value_error_str='an integer number', **kwargs):
            self._base = base
            self.value_error_str = value_error_str
            super(IntConvertor, self).__init__(self.value_error_str)

        def __call__(self, value):
            result = int(value, self._base)
            return result

        def __repr__(self):
            return 'IntConvertor(base=%d, value_error_str=%s)' % (self._base, self.value_error_str)

Convertors
----------

.. autoclass:: cooked_input.IntConvertor

.. autoclass:: cooked_input.FloatConvertor

.. autoclass:: cooked_input.BooleanConvertor

.. autoclass:: cooked_input.ListConvertor

.. autoclass:: cooked_input.DateConvertor

.. autoclass:: cooked_input.YesNoConvertor

.. autoclass:: cooked_input.TableConvertor


