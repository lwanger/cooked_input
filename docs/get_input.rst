.. currentmodule:: cooked_input

get_input
*********

cooked_input contains the top-level calls for the cooked_input library. Beginners can just use the `convenience functions <#id2>`_.

Exceptions:
===========

``cooked_input`` exceptions are generally only used for commands. See `GetInputCommand <#id1>`_ for more information on
using commands.

.. autoclass:: GetInputInterrupt

.. autoclass:: RefreshScreenInterrupt

.. autoclass:: PageUpRequest

.. autoclass:: PageDownRequest

.. autoclass:: FirstPageRequest

.. autoclass:: LastPageRequest

.. autoclass:: UpOneRowRequest

.. autoclass:: DownOneRowRequest


GetInputCommand:
================

.. autoclass:: GetInputCommand


GetInput:
=========

.. autoclass:: GetInput


.. automethod:: GetInput.get_input


.. automethod:: GetInput.process_value


Convenience Functions:
======================


A number of convenience functions are available to simplify getting the basic types of input. These functions create
a GetInput object with a parameter values for the type desired (e.g. hard code the convertor and set a reasonable prompt
and set of cleaners.) The convenience functions are just syntactic sugar for calls to GetInput, but simpler to use. For
instance, the following two function calls do the same thing::


    # GetInput version:
    gi = GetInput(prompt='Enter a whole number', convertor=IntConvertor())
    result = gi.get_input()

    # Convenience function:
    result = get_int(prompt='Enter a whole number')


Using the convenience functions you can get up and running in ``cooked_input`` very quickly.


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