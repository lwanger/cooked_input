.. currentmodule:: cooked_input

Convenience Functions
*********************

Using these convenience functions you can get up and running in ``cooked_input`` very quickly.
Most users can just use these convenience functions and never have to go deeper into the library.

The convenience functions can also take advantage of the rich set up `Cleaners <cleaners.html>`_,
`Convertors <convertors.html>`_, and `Validators <validators.html>`_ in the
``cooked_input`` library.

GetInput Convenience Functions
==============================

These functions create a :class:`GetInput` object with parameter values for the type desired (e.g. the
convertor and a reasonable prompt and cleaners.) The convenience functions are just syntactic sugar for
calls to :class:`GetInput`, but simpler to use. For instance, the following two versions calls do the same thing::


    # GetInput version:
    gi = GetInput(prompt='Enter a whole number', convertor=IntConvertor())
    result = gi.get_input()

    # Convenience function:
    result = get_int(prompt='Enter a whole number')


Common options
--------------

Every function below accepts the same set of :class:`GetInput` options, which is why their parameter
lists look long. **They are all optional and all keyword-only, and most calls use one or two** --
usually just ``prompt``::

    ci.get_string(prompt="What is your favorite color?")

The full set, in rough order of how often you will reach for them:

+-------------------------+------------------------------------------------------------------------+
| **Option**              | **What it does**                                                       |
+=========================+========================================================================+
| ``prompt``              | the text to prompt with. Each function has a sensible default.         |
+-------------------------+------------------------------------------------------------------------+
| ``required``            | **False** accepts a blank response and returns **None**.               |
+-------------------------+------------------------------------------------------------------------+
| ``default``             | the value to use when the response is blank.                           |
+-------------------------+------------------------------------------------------------------------+
| ``default_str``         | what to display for the default, when it differs from the value.       |
+-------------------------+------------------------------------------------------------------------+
| ``hidden``              | **True** keeps the typing off the screen -- for passwords.             |
+-------------------------+------------------------------------------------------------------------+
| ``retries``             | give up after this many bad attempts, raising :class:`MaxRetriesError`.|
+-------------------------+------------------------------------------------------------------------+
| ``commands``            | commands callable from the prompt, see :class:`GetInputCommand`.       |
+-------------------------+------------------------------------------------------------------------+
| ``error_callback``      | what to call when a value is rejected. Defaults to :func:`print_error`.|
+-------------------------+------------------------------------------------------------------------+
| ``convertor_error_fmt`` | how to word a conversion failure.                                      |
+-------------------------+------------------------------------------------------------------------+
| ``validator_error_fmt`` | how to word a validation failure.                                      |
+-------------------------+------------------------------------------------------------------------+

See :class:`GetInput` for the full description of each. An option these functions do not have raises
a ``TypeError``, so a misspelling is reported rather than quietly ignored.

``required`` and the return value
---------------------------------

These functions only ever return **None** for a blank response, and a blank response is only accepted
when ``required=False``. So ``get_int()`` always returns an ``int``, and only ``get_int(required=False)``
can hand back **None**::

    total = ci.get_int(prompt="How many?") + 1        # fine -- this is an int
    maybe = ci.get_int(prompt="How many?", required=False)
    if maybe is not None:                             # this one needs the check
        total = maybe + 1

Each function declares this to type checkers with a pair of :func:`typing.overload` signatures, so a
checker narrows the result for you and does not ask for a **None** test that can never fire. The
"Return type" shown for each function below is the underlying implementation's, which covers both
cases at once.


get_string
----------

.. autofunction:: get_string

get_int
-------

.. autofunction:: get_int

get_float
---------

.. autofunction:: get_float

get_boolean
-----------

.. autofunction:: get_boolean

get_date
--------

.. autofunction:: get_date

get_yes_no
----------

.. autofunction:: get_yes_no

get_money
----------

.. autofunction:: get_money

get_list
--------

.. autofunction:: get_list

get_input
---------

.. autofunction:: get_input

process_value
-------------

.. autofunction:: process_value


validate
--------

.. autofunction:: validate

Table Convenience Functions
===========================

These functions create a :class:`Table` object with everything needed to display a simple menu or table. The convenience
functions are just syntactic sugar for calls to :class:`Table`, but simpler to use. For instance, the following two
versions do the same thing::


    # GetInput version:
    menu_choices = [ TableItem('red'), TableItem('green'), TableItem('blue') ]
    menu = Table(rows=menu_choices, prompt='Pick a color')
    result = menu.get_table_choice()

    # Convenience function:
    result = get_menu(['red', 'green', 'blue'], prompt='Pick a color')


get_menu
--------

.. autofunction:: get_menu


create_rows
-----------

.. autofunction:: create_rows


create_table
------------

.. autofunction:: create_table


show_table
----------

.. autofunction:: show_table


get_table_input
---------------

.. autofunction:: get_table_input
