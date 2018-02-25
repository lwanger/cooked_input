.. currentmodule:: cooked_input

get_table
*********

`get_table` contains classes and functions to support text-based table and menus in `cooked_input`.

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


Command Action Functions:
=========================

The following pre-defined action functions can be used for commands (see :class:`GetInputCommand`):

first_page_cmd_action
---------------------

.. autofunction:: first_page_cmd_action


last_page_cmd_action
--------------------

.. autofunction:: last_page_cmd_action


prev_page_cmd_action
--------------------

.. autofunction:: prev_page_cmd_action


next_page_cmd_action
--------------------

.. autofunction:: next_page_cmd_action


scroll_up_one_row_cmd_action
----------------------------

.. autofunction:: scroll_up_one_row_cmd_action


scroll_down_one_row_cmd_action
------------------------------

.. autofunction:: scroll_down_one_row_cmd_action