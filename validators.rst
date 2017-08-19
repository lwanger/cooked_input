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



Validators
----------

Validator classes inherit from the Validator metaclass. They must be callable, with the __call__ dunder
method taking one parameter, the value. An example of a validator to verify that the input is exactly
a specified length looks like::

    class ExactLengthValidator(Validator):
        # check a value is exactly a length
        def __init__(self, length=None, **kwargs):
            self._length = length
            super(ExactLengthValidator, self).__init__(**kwargs)

        def __call__(self, value):
            # TypeError thrown if value does not implement __len__
            val_len = len(value)
            condition1 = (self._length is None or val_len == self._length)
            return True if condition1 else False

        def __repr__(self):
            return 'ExactLengthValidator(value=%s)' % (self._length)


.. autoclass:: ExactLengthValidator

.. autoclass:: InLengthValidator

.. autoclass:: ExactValueValidator

.. autoclass:: InRangeValidator

.. autoclass:: InChoicesValidator

.. autoclass:: NotInValidator

.. autoclass:: InAnyValidator

.. autoclass:: RegexValidator

.. autoclass:: PasswordValidator

.. autoclass:: ListValidator

helper functions:
-----------------

.. autofunction:: validate

