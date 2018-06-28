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
