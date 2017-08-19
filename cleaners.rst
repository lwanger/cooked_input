Cleaners
========

.. module::  cleaners

Cleaner classes for cleaning input before conversion and validation.


Cleaners
--------

Cleaner classes inherit from the Cleaner metaclass. They must be callable, with the __call__ dunder
method taking one parameter, the value. An example of a cleaner to change the input value to lower
case looks like::

    class LowerCleaner(Cleaner):
        def __init__(self, **kwargs):
            super(LowerCleaner, self).__init__(**kwargs)
            # initialize any specific state for the cleaner.

        def __call__(self, value):
            result = value.lower()
            return result


.. autoclass:: LowerCleaner

.. autoclass:: UpperCleaner

.. autoclass:: CapitalizeCleaner

.. autoclass:: StripCleaner

.. autoclass:: ReplaceCleaner

