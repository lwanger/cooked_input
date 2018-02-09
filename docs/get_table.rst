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


Convenience Functions:
======================


get_menu
--------

.. autofunction:: get_menu


get_table_input
---------------

.. autofunction:: get_table_input


first_page_cmd_action
---------------------

.. autofunction:: first_page_cmd_action