error_callbacks
***************



Creating Error functions:
=========================

Error functions are used by cooked_input to report errors from `convertors <convertors.html>`_ and 
`validators <validators.html>`_. Error functions take three parameters:

 * ``fmt_str``: a Python `format string <https://docs.python.org/3/library/string.html#formatspec>`_
   for the error. The format string can use the arguments **{value}** and **{error_content}**.
 * ``value``: the value that caused the error from the `convertor <convertors.html>`_ or 
   `validator <validators.html>`_.
 * ``error_content``: the particulars of the error message from the `convertor <convertors.html>`_ or
   `validator <validators.html>`_.

The following example prints errors to sys.stdout::

    def print_error(fmt_str, value, error_content):
        print(fmt_str.format(value=value, error_content=error_content))

An example of a convertor format string is as follows::

    generic_convertor_fmt = '{value} cannot be converted to {error_content}'

and similarly for validation::

    generic_validator_fmt = '{value} {error_content}'


error_callbacks:
================

log_error
---------

.. autofunction:: cooked_input.log_error


print_error
-----------

.. autofunction:: cooked_input.print_error


silent_error
------------

.. autofunction:: cooked_input.silent_error
