Cleaners
********

.. module::  cleaners

Cleaner classes for cleaning input before conversion and validation.


Creating Cleaners
=================

Cleaner classes inherit from the :class:`Cleaner` base class. They must be callable, with the ``__call__`` dunder
method taking one parameter, the value. An example of a cleaner to change the input value to lower
case looks like::

    class LowerCleaner(Cleaner):
        def __init__(self, **kwargs):
            # initialize any specific state for the cleaner.
            pass

        def __call__(self, value, error_callback, convertor_fmt_str):
            return value.lower()

Cleaners
========


CapitalizationCleaner
---------------------

.. autoclass:: cooked_input.CapitalizationCleaner
    :members:


ChoiceCleaner
-------------

.. autoclass:: cooked_input.ChoiceCleaner


RegexCleaner
------------

.. autoclass:: cooked_input.RegexCleaner


RemoveCleaner
-------------

.. autoclass:: cooked_input.RemoveCleaner


ReplaceCleaner
--------------

.. autoclass:: cooked_input.ReplaceCleaner


StripCleaner
------------

.. autoclass:: cooked_input.StripCleaner
