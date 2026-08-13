"""
Convenience functions for building tables and menus.

These wrap the :class:`Table` machinery in ``get_table.py``: ``create_rows`` and
``create_table`` build a table from a list of objects or dicts, ``show_table`` prints one, and
``get_table_input`` and ``get_menu`` put one on screen and return the choice. Most users need
nothing else.

Split out of ``get_table.py``, which had grown past 1500 lines holding both, mirroring the same
split of ``get_input.py`` into machinery and convenience functions.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""


from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from ._typing import CommandsArg, ErrorCallback, ItemFilter, RowAction
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .get_table import Table, TableItem, TableStyle, return_tag_action
from .get_table import RULE_NONE, TABLE_ADD_NONE, TABLE_RETURN_TABLE_ITEM
# GetInputCommand is not used in the code below, only in the ``CommandsArg`` annotation -- but
# that alias leaves the class name quoted (see ``_typing``), and a quoted forward reference is
# resolved in the module that *uses* the alias. get_table.py carries this same import for the
# same reason; without it sphinx_autodoc_typehints fails the -W docs build with "Cannot resolve
# forward reference" for every function here that takes ``commands``.
from .get_input import GetInputCommand  # noqa: F401


def create_rows(items: Iterable[Any] | Mapping[Any, Any], fields: Sequence[str],
                gen_tags: bool | None = None, item_data: dict[str, Any] | None = None,
                add_item_to_item_data: bool = False) -> list[TableItem]:
    """
    Create a list of TableItems from an iterable (items) of objects

    :param items: iterable containing items for the table.
    :param fields: list of field/attribute names to use as column values for each item.
    :param gen_tags: if **True** will generate sequentially numbered tags for table items, if False (default) uses
            first column value of each item for the row's tag.
    :param item_data: An optional dictionary to be copied and  attached to the :class:`TableItem` for the row.
    :param add_item_to_item_data: if **True** ``item_data['item']`` is set to `item`.

    :return: List[TableItem] of  table items (:class:`TableItem`)

    ``create_rows`` is a convenience function used to create a list of table items (:class:`TableItem`) for a
    ``cooked_input`` :class:`Table`. ``create_rows`` tries to make it easy to create the rows for a table from
    a list of data or a query.

    ``create_rows`` takes an iterable of ``items``, such as a list, dictionary or query. The items in ``items``
    can be just about anything too: objects, lists, dictionaries, tuples, or namedtuples.  ``create_rows`` also
    takes a list of ``fields`` with each item in the list the name of a field or attribute in the items. ``create_rows``
    iterates through ``items`` and add the value for each field as a column value for the table row.

    ``create_rows`` fetches the field data based on the following::

        1. If ``hasattr`` for the fields returns **True** (**__getattr__** is defined), uses ``getattr`` to retreive
            field values. This works nicely for class instances, named tuples, and database query results from an
            object-relationship mapper (ORM).
        2. If the items are dictionaries, uses ``get`` to retreive the value for the key matching the field name.
        3. If both of the previous methods fail, the first len(fields) values of the item are used (requires
            **__get_item__** to be defined.)

    .. note::

        Care is taken to make a single pass through the ``items`` iterable as some iterables are non-reentrant
        (e.g. generators and some database queries)


    Example usage - get a list of integers between 3 and 5 numbers long, separated by colons (:)::

        class Person(object):
            def __init__(self, first, last, age, shoe_size):
                self.first = first
                self.last = last
                self.age = age
                self.shoe_size = shoe_size

        people = [
            Person('John', 'Cleese', 78, 14),
            Person('Terry', 'Gilliam', 77, 10),
            Person('Eric', 'Idle', 75, 12),
        ]

        rows = create_rows(people, ['last', 'first', 'shoe_size'])
        Table(rows, ['First', 'Shoe Size'], tag_str='Last').show_table()

    ``create_rows`` is called by :func:`create_table` to create the table rows.
    """
    tis = []
    GET_ATTR, GET, GET_ITEM = range(3)
    fetch_method = None

    """
    This is a goofy way of doing things, and it would be a lot cleaner to check the types (Iterable, Mapping, etc.) But
    you can't do that in legacy Python (e.g. v2.7) as there is no Typing module. This will be cleaned this up when legacy 
    Python support is dropped.
    """
    if isinstance(items, dict):
        use_items = items.values()
    else:
        use_items = items

    for item in use_items:
        """
        Note: fetch_method is set in the first iteration of the loop as some items are not re-entrant (generators and
        queries from some databases.) If can only use __get_item__ (indexing into a list/array) it assumes the fields
        are in order of the list.
        """
        if item_data is None:
            use_item_data = None
        else:
            use_item_data = dict(item_data)

        if fetch_method is None:    # determine method to fetch items.
            if hasattr(item, fields[0]):
                fetch_method = GET_ATTR
            elif isinstance(item, dict):
                fetch_method = GET
            elif hasattr(item, '__getitem__'):
                fetch_method = GET_ITEM
            else:
                raise RuntimeError('create_rows cannot access data - item needs one of getattr, get, or __getitem__ defined.')

        if fetch_method == GET_ATTR:
            row_data = [ getattr(item, name) for name in fields ]
        elif fetch_method == GET:
            row_data = [ item.get(name) for name in fields ]
        elif fetch_method == GET_ITEM and len(item) >= len(fields):
            row_data = item[:len(fields)]
        else:
            raise RuntimeError(
                'create_rows cannot fetch field values - getattr, get, and __getitem__ all failed.')

        if gen_tags is True:
            tag = None
            use_row_data = row_data
        else:
            tag = row_data[0]
            use_row_data = row_data[1:]

        if add_item_to_item_data is True:
            if use_item_data is None:
                use_item_data = {}
            use_item_data['item'] = item

        tis.append(TableItem(col_values=use_row_data, tag=tag, item_data=use_item_data))

    return tis


def create_table(items: Iterable[Any] | Mapping[Any, Any], fields: Sequence[str],
                 field_names: Sequence[str] | None = None,
                 gen_tags: bool | None = None, item_data: dict[str, Any] | None = None,
                 add_item_to_item_data: bool = False, title: str | None = None,
                 prompt: str | None = None, default_choice: Any = None,
                 default_str: str | None = None,
                 default_action: str | RowAction = TABLE_RETURN_TABLE_ITEM,
                 style: TableStyle | None = None, *,
                 required: bool = True,
                 tag_str: str | None = None,
                 add_exit: bool | str = TABLE_ADD_NONE,
                 action_dict: dict[str, Any] | None = None,
                 case_sensitive: bool = False,
                 commands: CommandsArg = None,
                 refresh: bool = True,
                 item_filter: ItemFilter | bool | None = None,
                 header: str | None = None,
                 footer: str | None = None) -> Table:
    """
    Convenience function to create ``cooked_input`` a table.

    :param items: iterable containing items for the table.
    :param fields: list of field/attribute names to use as column values for each item.
    :param field_names: a list of strings to use for the names of the table columns.
    :param gen_tags: if **True** will generate sequentially numbered tags for table items, if False (default) uses
            first column value of each item for the row's tag.
    :param item_data: An optional dictionary to be copied and  attached to the :class:`TableItem` for the row.
    :param add_item_to_item_data: if **True** ``item_data['item']`` is set to `item`.
    :param title: an optional string to use as the title for the table.
    :param prompt: an optional string to use for the table prompt.
    :param default_choice: an optional default value to use for when getting input from the table.
    :param default_str: an optional string to display for the default choice value.
    :param default_action: the default action to take when a table item is picked. Defaults to **TABLE_RETURN_TABLE_ITEM***.
    :param style: an optional :class:`TableStyle` to use for the table.
    :param tag_str: string to use for the tag column name. Defaults to the name of whichever column
        became the tag -- see ``gen_tags`` above.
    :param required: see :class:`Table`.
    :param add_exit: see :class:`Table`.
    :param action_dict: see :class:`Table`.
    :param case_sensitive: see :class:`Table`.
    :param commands: see :class:`Table`.
    :param refresh: see :class:`Table`.
    :param item_filter: see :class:`Table`.
    :param header: see :class:`Table`.
    :param footer: see :class:`Table`.

    :return: an instance of a ``cooked_input`` :class:`Table`

    ``create_table`` is a convenience function used to create a ``cooked_input`` table (:class:`Table`) from
    a list of data or a query.

    ``create_table`` calls :func:`create_rows` to create the table rows. See :func:`create_rows` for an explanation
    of the: ``items``, ``fields``, ``gen_tags``, ``item_data``, and ``add_item_to_item_data`` parameters.

    See :class:`Table` for an explanation of the: ``title``, ``prompt``, ``default_choice``, ``default_str``,
        ``default_action``, ``style`` and keyword-only parameters.

    .. note::

        all items are created with the same ``default_action`` and ``item_data`` (with exception of adding the item
        to ``item_data['item']`` if ``add_item_to_item_data`` is **True**.)

    .. note::

        By default all items (rows) are visible and enabled. Rows can be hidden or disabled by setting an
        ``item_filter`` value in the ``options`` dictionary.

    Example usage - get a list of integers between 3 and 5 numbers long, separated by colons (:)::

        items = {
            1: {"episode": 1, "name": "Whither Canada?", "date": "5 October, 1969", "season": 1},
            2: {"episode": 4, "name": "Owl Stretching Time", "date": "26 October, 1969", "season": 1},
            3: {"episode": 15, "name": "The Spanish Inquisition", "date": "22 September, 1970", "season": 2},
            4: {"episode": 35, "name": "The Nude Organist", "date": "14 December, 1972", "season": 2}
        }

        fields = 'episode name date'.split()
        field_names = 'Episode Name Date'.split()
        tbl = create_table(items, fields, field_names, add_item_to_item_data=True, title='Episode List')
        choice = tbl.get_table_choice()
        item = choice.item_data["item"]
        print('{}: {}'.format(item['name'], item['season']))
    """
    use_tag_str = tag_str

    # `fields` names the columns when the caller supplied no display names of its own. Both
    # arms below only ever read from this one sequence; the previous form interleaved the
    # two sources, which meant every branch had to re-ask which one it was looking at -- and
    # left a field_names[1:] on a path where field_names could not be proved non-None.
    column_names = fields if field_names is None else field_names

    if gen_tags is True:
        use_field_names = column_names
        if use_tag_str is None:
            use_tag_str = ' '
    else:
        # Without generated tags the first column becomes the row tag, so it leaves the
        # table body and names the tag column instead.
        use_field_names = column_names[1:]
        if use_tag_str is None:
            use_tag_str = column_names[0]

    tis = create_rows(items, fields, gen_tags, item_data, add_item_to_item_data)
    # Dropped `show_cols=` and `show_border=` arguments here, taken from a `use_style` built
    # just above. Neither is a Table option -- they are TableStyle fields -- so back when this
    # call ended in **options they were accepted and silently discarded. The style has always
    # come from `style` alone, and `use_style` merely rebuilt the default TableStyle that Table
    # builds for itself when style is None.
    tbl = Table(tis, col_names=use_field_names, default_choice=default_choice,
                default_str=default_str, default_action=default_action, prompt=prompt, title=title,
                style=style, required=required, tag_str=use_tag_str, add_exit=add_exit,
                action_dict=action_dict, case_sensitive=case_sensitive, commands=commands,
                refresh=refresh, item_filter=item_filter, header=header, footer=footer)
    return tbl


def show_table(table: Table) -> None:
    """
    Displays a table without asking for input from the user.

    :param table: a :class:`Table` instance

    :return: None

    This took a ``**options`` bag it could not use: :meth:`Table.show_table` accepts no arguments, so
    every option raised ``TypeError: got an unexpected keyword argument``. A table's options are set
    when it is built, which is the only place they can affect what is drawn.
    """
    return table.show_table()


def get_table_input(table: Table, *,
                    prompt: str | None = None,
                    required: bool | None = None,
                    default: Any = None,
                    default_str: str | None = None,
                    hidden: bool = False,
                    retries: int | None = None,
                    commands: CommandsArg = None,
                    error_callback: ErrorCallback = print_error,
                    convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
                    validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> Any:
    """
    Get input value from a table of values.

    Typical use::

        ci.get_table_input(tbl, prompt="Which event type?")

    :param table: a :class:`Table` instance
    :param prompt: the prompt for choosing a table value. Defaults to the table's own ``prompt``.
    :param required: requires an entry if **True**, exits the table on blank entry if **False**
    :param default: the default value to use
    :param default_str: an optional string to display for the default table selection
    :param hidden: **True** to keep the typed choice off the screen
    :param retries: maximum attempts before raising :class:`MaxRetriesError`
    :param commands: a dictionary of commands for the table
    :param error_callback: called when a choice is rejected. Defaults to :func:`print_error`
    :param convertor_error_fmt: format string for `convertor <convertors.html>`_ errors
    :param validator_error_fmt: format string for `validator <validators.html>`_ errors

    :return: the value from calling :func:`Table.get_table_choice` on the table. The return type
        is **Any** because it is whatever the selected row's action function returns.

    :raises TypeError: if given an option this function does not have

    These are the options for the one prompt this call makes, not options for building the table --
    see :meth:`Table.get_table_choice`, which this hands them to unchanged.
    """
    return table.get_table_choice(prompt=prompt, required=required, default=default,
                                  default_str=default_str, hidden=hidden, retries=retries,
                                  commands=commands, error_callback=error_callback,
                                  convertor_error_fmt=convertor_error_fmt,
                                  validator_error_fmt=validator_error_fmt)


def get_menu(choices: Iterable[Any], title: str | None = None, prompt: str | None = None,
             default_choice: Any = None, add_exit: bool | str = False,
             style: TableStyle | None = None, *,
             default_action: str | RowAction = return_tag_action,
             required: bool = True,
             tag_str: str = '',
             action_dict: dict[str, Any] | None = None,
             case_sensitive: bool = False,
             commands: CommandsArg = None,
             refresh: bool = True,
             item_filter: ItemFilter | bool | None = None,
             header: str | None = None,
             footer: str | None = None) -> Any:
    """
    :param choices: the list of text strings to use for the menu items
    :param title: a title to use for the menu
    :param prompt: the prompt string used when asking the user for the menu selection
    :param default_choice: an optional default item to select. Either the text of one of the
        ``choices`` or its position in the menu, counting from 1.
    :param add_exit: add an exit item if `True` or not if `False` (default)
    :param style: a :class:`TableStyle` defining the look of the menu.
    :param default_action: the action to take when a menu item is picked. Defaults to returning the
        item's tag, which is its one-based position in the menu.
    :param required: see :class:`Table`.
    :param tag_str: see :class:`Table`.
    :param action_dict: see :class:`Table`.
    :param case_sensitive: see :class:`Table`.
    :param commands: see :class:`Table`.
    :param refresh: see :class:`Table`.
    :param item_filter: see :class:`Table`.
    :param header: see :class:`Table`.
    :param footer: see :class:`Table`.

    :return: the result of calling :func:`Table.get_table_choice` on the menu table. Will return the index (one based) of
        the choice selected, unless a different ``default_action`` is given. Returns 'exit' if the input
        value is `None` or the menu was exited.

    This is a convenience function to create a Table that acts as a simple menu. It takes a list of text strings
    to use for the menu items, and returns the text string of the item picked. `get_menu` is just syntactic sugar
    for calls to the :class:`Table` class, but simpler to use.
    """
    menu_choices = [TableItem(choice) for choice in choices]

    if default_choice is None:
        default_str = None
    else:
        default_str = ' (return for {})'.format(default_choice)

    default_idx = None

    if style is None:
        use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    else:
        use_style = style

    if default_choice is not None:
        # Fixing: the `break` used to sit at the end of the try body, so it ran on the
        # first item whether or not anything had matched. Matching by value survived that
        # only by accident -- int('green') raised ValueError before the break was reached
        # and the handler swallowed it -- while a numeric default_choice like '2' never
        # resolved at all and the menu silently had no default. The numeric comparison was
        # also off by one, against 0-based positions rather than the 1-based tags the table
        # assigns. Interpreting the choice as a number once, up front, keeps the loop plain.
        try:
            numeric_choice = int(default_choice)
        except (TypeError, ValueError):
            numeric_choice = None

        # Menu items are built as TableItem(choice) just above, so mc.tag is always None
        # and the menu's tags are the 1-based positions the table assigns. Matching on
        # mc.tag, as the Table path does, would be dead code here.
        for i, mc in enumerate(menu_choices, start=1):
            if mc.values[0] == default_choice or i == numeric_choice:
                default_idx = i
                break

    menu = Table(menu_choices, title=title, prompt=prompt, default_choice=default_idx, default_str=default_str,
                default_action=default_action, add_exit=add_exit, style=use_style, required=required,
                tag_str=tag_str, action_dict=action_dict, case_sensitive=case_sensitive,
                commands=commands, refresh=refresh, item_filter=item_filter, header=header,
                footer=footer)
    result = menu.get_table_choice()

    # Fixing: a second branch here tested `result == 'exit'`, which could never be true --
    # do_action handed back the TableItem for the exit row and a TableItem never equals a
    # string, so get_menu returned the row instead of the documented 'exit'. do_action now
    # returns None for an exit row, the same as choosing no row, so this one branch covers
    # both ways of leaving the menu.
    if result is None:
        return 'exit'

    return result
