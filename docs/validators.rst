Validators
==========

.. module::  validators

The last step in cooked input is to validate that the entered input is valid. When called, Validators return True if
the input passes the validation (i.e. is valid), and False otherwise.



Creating Validators
-------------------

Validator classes inherit from the Validator metaclass. They must be callable, with the __call__ dunder
method taking three parameters: the value to validate, a function to call when an error occurs and the format string
for the error function. See the [error_callbacks] for more information on error functions and their format strings.

An example of a validator to verify that the input is exactly a specified length looks like::

    class ExactLengthValidator(Validator):
        def __init__(self, length=None, **kwargs):
            self._length = length
            super(ExactLengthValidator, self).__init__(**kwargs)

        def __call__(self, value, error_callback, validator_fmt_str):
            val_len = len(value)
            condition1 = (self._length is None or val_len == self._length)
            return True if condition1 else False

        def __repr__(self):
            return 'ExactLengthValidator(value=%s)' % (self._length)

Note: There are a large number of Boolean validation functions available from the validus project. These can be used as
cooked_input validation functions by wrapping them in a SimpleValidator. For instance, to use validus to validate an email address::

    from validus import isemail
    email_validator = SimpleValidator(isemail, name='email')
    email = get_input(prompt='enter a valid Email address', validators=email_validator)


for more information on validus see: https://github.com/shopnilsazal/validus


Validators
==========

ExactLengthValidator
--------------------

.. autoclass:: cooked_input.ExactLengthValidator

InLengthValidator
-----------------

.. autoclass:: cooked_input.InLengthValidator

ExactValueValidator
-------------------

.. autoclass:: cooked_input.ExactValueValidator

InRangeValidator
----------------

.. autoclass:: cooked_input.InRangeValidator

InChoicesValidator
------------------

.. autoclass:: cooked_input.InChoicesValidator

NotInValidator
--------------

.. autoclass:: cooked_input.NotInValidator

InAnyValidator
--------------

.. autoclass:: cooked_input.InAnyValidator

SimpleValidator
---------------

.. autoclass:: cooked_input.SimpleValidator

RegexValidator
--------------

.. autoclass:: cooked_input.RegexValidator

PasswordValidator
-----------------

.. autoclass:: cooked_input.PasswordValidator

ListValidator
-------------

.. autoclass:: cooked_input.ListValidator
