Validators
==========

.. module::  validators

The last step in cooked input is to validate that the entered input is valid. When called, Validators return True if
the input passes the validation (i.e. is valid), and False otherwise.

Note: There are a large number of validator functions available from the validus project. These can be used as
cooked_input validation functions. For instance, to use validus to validate an email address::

    from validus import isemail
    email = get_input(prompt='enter a valid Email address', validators=isemail)

for more information on validus see: https://github.com/shopnilsazal/validus



Creating Validators
-------------------

Validator classes inherit from the Validator metaclass. They must be callable, with the __call__ dunder
method taking one parameter, the value. An example of a validator to verify that the input is exactly
a specified length looks like::

    class ExactLengthValidator(Validator):
        def __init__(self, length=None, **kwargs):
            self._length = length
            super(ExactLengthValidator, self).__init__(**kwargs)

        def __call__(self, value):
            val_len = len(value)
            condition1 = (self._length is None or val_len == self._length)
            return True if condition1 else False

        def __repr__(self):
            return 'ExactLengthValidator(value=%s)' % (self._length)


Validators
----------

.. autoclass:: cooked_input.ExactLengthValidator

.. autoclass:: cooked_input.InLengthValidator

.. autoclass:: cooked_input.ExactValueValidator

.. autoclass:: cooked_input.InRangeValidator

.. autoclass:: cooked_input.InChoicesValidator

.. autoclass:: cooked_input.NotInValidator

.. autoclass:: cooked_input.InAnyValidator

.. autoclass:: cooked_input.RegexValidator

.. autoclass:: cooked_input.PasswordValidator

.. autoclass:: cooked_input.ListValidator
