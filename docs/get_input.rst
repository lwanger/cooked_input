get_input
*********

github archive: https://github.com/lwanger/cooked_input


cooked_input contains the top-level calls for the cooked_input library.

Fundamental Functions:
======================

The basis of cooked_input is in a handful of functions:

get_input
---------

.. autofunction:: cooked_input.get_input


get_table_input
---------------

.. autofunction:: cooked_input.get_table_input

validate
--------

.. autofunction:: cooked_input.validate

process_value
-------------

.. autofunction:: cooked_input.process_value

convenience functions:
======================

A number of convenience functions are available to simplify geting the basic types of input. These functions set default
parameter values for the type desired (e.g. hard code the convertor and set a reasonable prompt and set of cleaners.)
The convenience functions are just syntactic sugar for calls to get_input, but simpler to use. For
instance, the following two function calls do the same thing::

    # get_input version:
    result = get_input(prompt='Enter a whole (integer) number', convertor=IntConvertor())

    # Convenience function:
    result = get_int()

get_string
----------

.. autofunction:: cooked_input.get_string

get_int
-------

.. autofunction:: cooked_input.get_int

get_float
---------

.. autofunction:: cooked_input.get_float

get_boolean
-----------

.. autofunction:: cooked_input.get_boolean

get_date
--------

.. autofunction:: cooked_input.get_date

get_yes_no
----------

.. autofunction:: cooked_input.get_yes_no

get_list
--------

.. autofunction:: cooked_input.get_list
