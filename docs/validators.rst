Validators
**********

.. module::  validators

The last step in cooked input is to validate that the entered input is valid. When called, Validators return True if
the input passes the validation (i.e. is valid), and False otherwise.


Creating Validators
===================

Validator classes inherit from the :class:`Validator`  base class. They must be a callable, and take three parameters:
the ``value`` to validate, a function to call when an error occurs and a format string
for the error function. See `error callbacks <error_callbacks.html>`_    for more information on error functions and their
format strings.

An example of a validator to verify that the input is exactly a specified length looks like::

    class LengthValidator(Validator):
        def __init__(self, min_len=None, max_len=None):
            self._min_len = min_len
            self._max_len = max_len

        def __call__(self, value, error_callback, validator_fmt_str):
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


.. note::
    There are a large number of Boolean validation functions available from the `validus <https://shopnilsazal.github.io/validus/>`_
    project. These can be used as cooked_input validation functions by wrapping them in a :class:`SimpleValidator`. For
    instance, to use ``validus`` to validate an email address::

        from validus import isemail
        email_validator = SimpleValidator(isemail, name='email')
        email = get_input(prompt='enter a valid Email address', validators=email_validator)

Validators
==========

AnyOfValidator
--------------

.. autoclass:: cooked_input.AnyOfValidator


ChoiceValidator
---------------

.. autoclass:: cooked_input.ChoiceValidator


EqualToValidator
-------------------

.. autoclass:: cooked_input.EqualToValidator


IsFileValidator
---------------

.. autoclass:: cooked_input.IsFileValidator


LengthValidator
---------------

.. autoclass:: cooked_input.LengthValidator


ListValidator
-------------

.. autoclass:: cooked_input.ListValidator


NoneOfValidator
---------------

.. autoclass:: cooked_input.NoneOfValidator


PasswordValidator
-----------------

.. autoclass:: cooked_input.PasswordValidator


RangeValidator
----------------

.. autoclass:: cooked_input.RangeValidator


RegexValidator
--------------

.. autoclass:: cooked_input.RegexValidator


SimpleValidator
---------------

.. autoclass:: cooked_input.SimpleValidator