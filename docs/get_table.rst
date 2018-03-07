.. currentmodule:: cooked_input

Tables and Menus
****************

The :class:`TableItem` and :class:`Table` support text-based tables and menus in `cooked_input`.

.. note::

 Using the :class:`Table` class is for more advanced users, Beginners can just use
 the :func:`get_menu` and :func:`get_table_input` `convenience functions <get_input_convenience.html>`_.

TableItem:
==========

.. autoclass:: TableItem


Table:
======

.. autoclass:: Table

.. automethod:: Table.get_table_choice

.. automethod:: Table.run

.. automethod:: Table.get_num_rows

.. automethod:: Table.get_row

.. automethod:: Table.get_action

.. automethod:: Table.do_action

.. automethod:: Table.show_rows

.. automethod:: Table.page_up

.. automethod:: Table.page_down

.. automethod:: Table.goto_home

.. automethod:: Table.goto_end

.. automethod:: Table.scroll_up_one_row

.. automethod:: Table.scroll_down_one_row

.. automethod:: Table.refresh_screen

.. automethod:: Table.refresh_items


Table Action Functions:
=======================

The following pre-defined action functions can be used for the action for :class:`Tables` and :class:`TableItem`:

return_table_item_action
------------------------

.. autofunction:: return_table_item_action

return_row_action
-----------------

.. autofunction:: return_row_action


return_tag_action
------------------

.. autofunction:: return_tag_action

return_first_col_action
-----------------------

.. autofunction:: return_first_col_action

