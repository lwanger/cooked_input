get_menu
********

`get_menu` contains classes and functions to support text-based menus in `cooked_input`.

TableItem:
==========

.. autofunction:: cooked_input.TableItem

DynamicTableItem:
=================

.. autofunction:: cooked_input.DynamicTableItem

Table:
======

.. autofunction:: cooked_input.Table

convenience functions:
======================

The `get_menu` convenience function is provided to simplify creating a basic menu. `get_menu` takes a list of text strings
to use for the menu items, and returns the text string of the item picked. `get_menu` is just syntactic sugar for calls to
the Menu class, but simpler to use.

get_menu
--------

.. autofunction:: cooked_input.get_menu