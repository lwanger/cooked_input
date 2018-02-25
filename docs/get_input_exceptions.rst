.. currentmodule:: cooked_input

Exceptions
**********

``cooked_input`` defines a number of custom exceptions. These are mainly used for `tables <get_table>`_ and
`commands <get_input_commands>`_.


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
