.. currentmodule:: cooked_input

Exceptions
**********

``cooked_input`` defines a number of custom exceptions. These are mainly used for `tables <get_table>`_ and
`commands <get_input_commands>`_.


``cooked_input`` exceptions are generally only used for commands. See `GetInputCommand <#id1>`_ for more information on
using commands.

ConvertorError:
---------------

.. autoclass:: ConvertorError

MaxRetriesError:
----------------

.. autoclass:: MaxRetriesError

ValidationError:
----------------

.. autoclass:: ValidationError

GetInputInterrupt:
------------------

.. autoclass:: GetInputInterrupt

RefreshScreenInterrupt:
-----------------------

.. autoclass:: RefreshScreenInterrupt

PageUpRequest:
--------------

.. autoclass:: PageUpRequest

PageDownRequest:
----------------

.. autoclass:: PageDownRequest

FirstPageRequest:
-----------------

.. autoclass:: FirstPageRequest

LastPageRequest:
----------------

.. autoclass:: LastPageRequest

UpOneRowRequest:
----------------

.. autoclass:: UpOneRowRequest

DownOneRowRequest:
------------------

.. autoclass:: DownOneRowRequest
