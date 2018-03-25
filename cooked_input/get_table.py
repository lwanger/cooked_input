from __future__ import print_function

"""
get_table - table/menu system for cooked_input

TODO:
    - navigation keys - looking for a good solution to capture keys like PageDown and bind them to functions. Curses 
    doesn't come on Windows.
    - Add more formatting to tables - borders, text styles, foreground and background colors, title, header, footer. 

Len Wanger, 2017
"""

import sys
import string

import veryprettytable as pt

from cooked_input import get_input
from cooked_input import GetInputInterrupt, RefreshScreenInterrupt
from cooked_input import PageUpRequest, PageDownRequest, FirstPageRequest, LastPageRequest, UpOneRowRequest, DownOneRowRequest

from .input_utils import put_in_a_list, isstring
from .cleaners import CapitalizationCleaner, StripCleaner, ChoiceCleaner
from .convertors import ChoiceConvertor
from .validators import ChoiceValidator


# Enumerated values for tables:
TABLE_ITEM_DEFAULT = 'default'
TABLE_ITEM_EXIT = 'exit'
TABLE_ITEM_RETURN = 'return'

TABLE_ADD_EXIT = 'exit'
TABLE_ADD_RETURN = 'return'
TABLE_ADD_NONE = 'none'

TABLE_RETURN_TAG = 'tag'
TABLE_RETURN_FIRST_VAL = 'first_value'
TABLE_RETURN_ROW = 'row'
TABLE_RETURN_TABLE_ITEM = 'table_item'

RULE_FRAME = pt.FRAME
RULE_HEADER = pt.HEADER
RULE_ALL = pt.ALL
RULE_NONE = pt.NONE

# Supplied table actions
def return_table_item_action(row, action_dict):
    """
    Action function for Tables. This function returns the TableItem instance. Used by the *TABLE_RETURN_TABLE_ITEM* action.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data for the selected row of the table.
    """
    return row


def return_row_action(row, action_dict):
    """
    Default action function for Tables. This function returns the whole row of data. Used by the *TABLE_RETURN_ROW* action.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data values for the selected row of the table.
    """
    return row.values


def return_tag_action(row, action_dict):
    """
    Default action function for tables. This function returns the tag for the row of data. Used by the *TABLE_RETURN_TAG* action.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: The tag for the selected row of the table.
    """
    return row.tag


def return_first_col_action(row, action_dict):
    """
    Default action function for tables. This function returns the first data column value for the row of data. Used by the *TABLE_RETURN_FIRST_VAL* action.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: The first value from the list of data values for the selected row of the table.
    """
    return row.values[0]


# command actions for supporting table pagination
def first_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the first (home) page in a paginated table. This command raises a :class:`FirstPageRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise FirstPageRequest


def last_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the last (end) page in a paginated table. This command raises a :class:`LastPageRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise LastPageRequest


def next_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the next page in a paginated table. This command raises a :class:`PageDownRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise PageDownRequest


def prev_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the previous page in a paginated table. This command raises a :class:`PageUpRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise PageUpRequest


def scroll_up_one_row_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to scroll up one row in a paginated table. This command raises a :class:`UpOneRowRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise UpOneRowRequest


def scroll_down_one_row_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to scroll down one row in a paginated table. This command raises a :class:`DownOneRowRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise DownOneRowRequest


#
# Class definitions for tables
#
class TableItem(object):
    """
    TableItem is used to represent individual rows in a table. This is also often used for menu items.

    :param col_values: A list of values the row's columns.
    :param tag:  a value that can be used to choose the item. If None, a default tag will be assigned by the Table
        The tag is often an integer of the row number, a database ID, or a textual tag.
    :param action:  the action to take when the item is selected.
    :param item_data:  a dictionary containing addtional contextual data for the table row. This is not displayed as
        part of the table item but can be used for processing actions. For instance, it can be used to store a database
        ID associated with the item. item_data is also used for item filters.
    :param hidden:  The table row is hidden if True, or visible if False (default). Hidden table items are still
        selectable, unless the enabled attribute is False.
    :param enabled:  The table row is selectable if True (default), and not selectable if False

    TableItem actions:

        The table item action specifies what to do when a table item is selected. By default the table item's tag value
        is returned. The action can be one of the default actions listed in the following table or a custom action can
        be provided:

        +--------------------+--------------------------------------------------------------------------+
        | value              | action                                                                   |
        +--------------------+--------------------------------------------------------------------------+
        | TABLE_ITEM_DEFAULT |  use default method to handle the table item (e.g. use the parent        |
        |                    |  table's default_action handler function)                                |
        +--------------------+--------------------------------------------------------------------------+
        | TABLE_ITEM__EXIT   |  selecting the table row should exit (ie exit the menu)                  |
        +--------------------+--------------------------------------------------------------------------+
        | TABLE_ITEM__RETURN |  selecting the table row should return (used to return from a submenu)   |
        +--------------------+--------------------------------------------------------------------------+

        In addition to the values in the table above, the action can be any callable that takes the following
        parameters:

        :param row: The TableItem instance selected (i.e. this table item)
        :param action_dict:  The parent table's action_dict.

        For example::

            def example_action(row, action_dict):
                print('Example action called for item {}'.format(row.tag))
    """
    def __init__(self, col_values, tag=None, action=TABLE_ITEM_DEFAULT, item_data=None, hidden=False, enabled=True):

        self.values = put_in_a_list(col_values)
        self.tag = tag
        self.action = action
        self.item_data = item_data
        self.hidden = hidden
        self.enabled = enabled

    def __repr__(self):
        return 'TableItem(col_values={}, tag={}, action={}, item_data={}, hidden={}, enabled={})'.format(self.values, self.tag,
                                                                                                         self.action, self.item_data, self.hidden, self.enabled)


class Table(object):
    """
    The Table class is used to choose a value from a table of data. Each row of data has the same number of
    columns (specified by the col_name parameter) as is represented by a TableItem istance. One of the major uses of
    Tables is for menus.

    :param rows: The rows of the table. Each row is a TableItem istance.
    :param col_names: An optonal list of the column names for the table. If no list is given the number of columns is
                        determined by the length of the data list for the first row (TableItem).
    :param title: An optional title for the table.
    :param prompt: The prompt for choosing a table value.
    :param default_choice: An optional default tag value to use for the table selection.
    :param default_str: An optional string to display for the defailt table selection.
    :param default_action: The default action to take when a table item is selected. See below for details.
    :param rows_per_page: The maximum number of rows to display in the table. Used to paginate tables.
    :param options: see below for a list of valid options

    Options:

        **required**:    requires an entry if True, exits the table on blank entry if False.

        **add_exit**:    automatically adds a TableItem to exit the menu (MENU_ADD_EXIT - default) or return to the
                                parent table/menu (MENU_ADD_RETURN), or not to add a TableItem at all (False). Used to
                                exit menus or return from sub-menus.

        **action_dict**: a dictionary of values to pass to action functions. Used to provide context to the action.
                                Helpful to provide items such as data base sessions, user credentials, etc.

        **case_sensitive**:  whether choosing table items should be case sensitive (True) or not (False - default)

        **commands**:    a dictionary of commands for the table. For each entry, the key is the command and the value
                                the action to take for the command. See GetInput and GetInputCommand for further details

        **item_filter**: a function used to determine which table items to display. Displays all items if None. See below for more details.

        **refresh**: refresh table items each time the table is shown (True - default), or just when created (False). Useful for dynamic tables

        **header**:  a format string to print before the table, can use any value from action_dict as well as pagination information

        **footer**:  a format string to print after the table, can use any values from action_dict as well as pagination information

        **show_border**:  if True (default) shows a border around the table

        **show_cols**:  if True (default) shows a the column names at the top of the table
        
        **hrules**:  whether to draw horizontal lines between rows. Values allowed: RULE_FRAME, RULE_HEADER, RULE_ALL and RULE_NONE

        **vrules**:  whether to draw vertical lines between rows. Values allowed: RULE_FRAME, RULE_HEADER, RULE_ALL and RULE_NONE

    Table default actions:

        Each table has a default action to take when an item is selected. The action can be a callable or a value from
        the table below. The Table's default action is called if the If the selected row (TableItem) has its action
        set to TABLE_DEFAULT_ACTION, otherwise the action for the selected TableItem is called. Standard values for the
        Table default action are:

        +--------------------------------+---------------------------------------------------------+
        | value                          | action                                                  |
        +--------------------------------+---------------------------------------------------------+
        | TABLE_DEFAULT_ACTION_TAG       | return the selected row's tag.                          |
        +--------------------------------+---------------------------------------------------------+
        | TABLE_DEFAULT_ACTION_FIRST_VAL | return the first data column value of the selected row. |
        +--------------------------------+---------------------------------------------------------+
        | TABLE_DEFAULT_ACTION_ROW       | return the list of column values for the selected row.  |
        +--------------------------------+---------------------------------------------------------+
        | TABLE_DEFAULT_ACTION_ITEM      | return the TableItem instance for the selected row.     |
        +--------------------------------+---------------------------------------------------------+

        In addition to the values in the table above, the action can be any callable that takes the following
        parameters:

            **row**: The TableItem instance selected (i.e. this table item)

            **action_dict**:  The parent table's action_dict.

            For example::

                def example_action(row, action_dict):
                    print('Example action called for item {}'.format(row.tag))


    item filters:

        The item filter provides a function that determines which table items are hidden and/or enabled in the table.
        It is a callable that takes the following input parameters:

            **item**:   the TableItem instance

            **action_dict**: the action_dict for the Table

        and returns a tuple of (hidden, enabled) for the item (TableItems).

        For example, a menu can have choices that are visible and enabled only for user's who are part of the
        administrator group::

            def user_role_filter(row, action_dict):
                if row.item_data is None:
                    return  (False, True)

                for role in action_dict['user'].roles:
                    if role in row.item_data['roles']:
                        return  (False, True)

                return (True, False)

            action_dict = {'user_roles': ['admin', 'users']}
            admin_only = {'roles': {'admin'} }
            mi1 = TableItem('Add a new user', action=user_add_action, item_data=admin_only)
            mi2 = TableItem('list users', action=user_list_action)
            menu_items = [mi1, mi2]
            menu = Table(menu_items, action_dict=action_dict, item_filter=user_role_filter)
    """

    def __init__(self, rows, col_names=None, title=None, prompt=None, default_choice=None, default_str=None,
                 default_action=None, rows_per_page=20, **options):

        try:
            self.required = options['required']
        except KeyError:
            self.required = True

        try:
            add_exit = options['add_exit']
            if add_exit in { True, False, TABLE_ADD_EXIT, TABLE_ADD_RETURN }:
                self.add_exit = add_exit
            else:
                print('Table:__init__: ')
                raise RuntimeError('Table: unexpected value for add_exit option ({})'.format(add_exit))
        except KeyError:
            #self.add_exit = TABLE_ADD_EXIT
            self.add_exit = TABLE_ADD_NONE

        try:
            self.action_dict = options['action_dict']
        except KeyError:
            self.action_dict = {}

        try:
            self.case_sensitive = options['case_sensitive']
        except KeyError:
            self.case_sensitive = False

        try:
            self.commands = options['commands']
        except KeyError:
            self.commands = None

        try:
            self.refresh = options['refresh']
        except KeyError:
            self.refresh = True

        try:
            self.item_filter = options['item_filter']
        except KeyError:
            self.item_filter = None

        try:
            self.show_border = options['show_border']
        except KeyError:
            self.show_border = True

        try:
            self.show_cols = options['show_cols']
        except KeyError:
            self.show_cols = True

        try:
            self.header = options['header']
        except KeyError:
            self.header = None

        try:
            self.footer = options['footer']
        except KeyError:
            self.footer = None

        try:
            self.hrules = options['hrules']
        except KeyError:
            self.hrules = RULE_FRAME

        try:
            self.vrules = options['vrules']
        except KeyError:
            self.vrules = RULE_FRAME

        if prompt is None:
            self.prompt = 'Choose a table item'
        else:
            self.prompt = prompt

        self.options = options
        self.title = title
        self.default_choice = default_choice
        self.default_str= default_str

        if default_action is None or default_action == 'tag':
            self.default_action = return_tag_action
        elif default_action == 'first_value':
            self.default_action = return_first_col_action
        elif default_action == 'row':
            self.default_action = return_row_action
        elif default_action == 'table_item':
            self.default_action = return_table_item_action
        else:
            self.default_action = default_action

        self.rows_per_page = rows_per_page
        self._table_items = put_in_a_list(rows)  # the original, raw table items for the table
        self._rows = []  # the expanded, refreshed table items for the table used to create the pretty table
        self.table = pt.VeryPrettyTable()  # the pretty table to display

        if col_names is None:
            num_cols = len(self._table_items[0].values)
            field_names = ['col {}'.format(i) for i in range(1, num_cols+1)]
        elif isstring(col_names):
            field_name_list = col_names.split()
            field_names = field_name_list
            num_cols = len(field_name_list)
        else:
            field_names = col_names
            num_cols = len(field_names)

        if len(field_names) != num_cols:
            raise RuntimeError('Table: number of column names does not match number of columns in the table'.format())

        self.field_names = ['tag'] + field_names
        self.table.field_names = ['tag'] + field_names + ['action']

        #self.table.set_style(pt.PLAIN_COLUMNS)
        self.table.set_style(pt.DEFAULT)
        #self.table.border = False
        self.table.border = self.show_border
        #elf.table.header = False
        self.table.header = self.show_cols
        self.table.align = 'l'
        self.table.align['tag'] = 'r'
        # self.tbl.left_padding_width = 2
        self.table.hrules = self.hrules
        self.table.vrules = self.vrules

        if self.refresh is False:   # set up rows to start as won't be refreshed each time called
            self.refresh_items(rows=rows, add_exit=True, item_filter=self.item_filter)

        self.show_rows(0)


    def __repr__(self):
        return 'Table(rows={}, col_name={}, title={}, prompt={}, default_choice={}, action_dict={})'.format(self._table_items,
                                            self.field_names, self.title, self.prompt, self.default_choice, self.action_dict)

    def get_num_rows(self):
        """
        Get the number of rows in the table.

        :return: the number of rows in the table
        """
        return len(self._rows)

    def get_row(self, tag):
        """
        Get the number of rows in the table.

        :return: the number of rows in the table
        """
        for row in self._rows:
            if row.tag == tag:
                return row
        raise ValueError('Table.get_row: tag ({}) not in the table'.format(tag))

    def get_action(self, tag):
        """
        Return the action callback function for the first row matching the specified tag.

        :param tag: the tag to search for
        :return: the action for the first row containing the tag. Raises ValueError if the tag is not found/
        """
        row = self.get_row(tag)
        return row.action

    def do_action(self, row):
        """
        Call the action function for the specified row

        :param row: the row (TableItem) of the table to call the action on

        :return:  returns the return value for the action. Returns the original row if no action is defined for the row.

        The action is called with the following parameters:

            :param row: The TableItem instance selected (i.e. this table item)
            :param action_dict:  The parent table's action_dict.
        """
        action = row.action
        if callable(action):
            return action(row, self.action_dict)
        elif action == 'default' and self.default_action is not None:
            return self.default_action(row, self.action_dict)
        else:
            return row

    def show_rows(self, start_row):
        """
        Set the starting row for to display in the table. Last row shown is the start_row plus the number of rows per
        page (or the last row if start_row is withing rows_per_page of the end of the table).

        :param start_row:

        :return: None
        """
        # set the starting and ending rows to show
        table_max_rows = self.get_num_rows()
        if start_row > table_max_rows - self.rows_per_page:
            start_row = table_max_rows - self.rows_per_page

        if start_row < 1:
            self.table.start = 0
        else:
            self.table.start = start_row

        table_end = self.table.start + self.rows_per_page
        if table_end > table_max_rows:
            table_end = table_max_rows

        self.table.end = table_end

    # def refresh_buffer(self, buffer):
    #     if buffer:
    #         buffer.text = self.table.get_string()
    #     else:
    #         print(self.table.get_string())
    #         print()
    #         raise RefreshScreenInterrupt


    def page_up(self):
        """
        Display the previous page of the table (if available)

        :return: None
        """
        self.show_rows(self.table.start - self.rows_per_page)
        print(self.table.get_string())

    def page_down(self):
        """
        Display the next page of the table (if available)

        :return: None
        """
        self.show_rows(self.table.start + self.rows_per_page)
        print(self.table.get_string())

    def goto_home(self):
        """
        Display the first page of the table

        :return: None
        """
        self.show_rows(0)
        print(self.table.get_string())

    def goto_end(self):
        """
        Display the last page of the table

        :return: None
        """
        self.show_rows(self.get_num_rows() - self.rows_per_page)
        print(self.table.get_string())

    def scroll_up_one_row(self):
        """
        Display the one row earlier in the table (if available)

        :return: None
        """
        self.show_rows(self.table.start + 1)
        print(self.table.get_string())

    def scroll_down_one_row(self):
        """
        Display the one row later in the table (if available)

        :return: None
        """
        self.show_rows(self.table.start - 1)
        print(self.table.get_string())


    def _prep_get_input(self, force_refresh=False):
        """
        Internal function to prepare the table for getting input. Refreshes the tabl (for dynamic tables) and prepares
        the choices, cleaners, covertor and validators.

        :return: a tuple of (choices, cleaners, convertor, validator) to use for getting input from the table.
        """
        if self.refresh or force_refresh:
            self.refresh_items(self._table_items, self.add_exit, self.item_filter)

        if self.case_sensitive:
            choices = {str(item.tag): i for i, item in enumerate(self._rows) if item.enabled is True}
        else:
            choices = {str(item.tag).lower(): i for i, item in enumerate(self._rows) if item.enabled is True}

        cleaners = [StripCleaner()]
        if not self.case_sensitive:
            cleaners.append(CapitalizationCleaner('lower'))
        cleaners.append(ChoiceCleaner(choices))

        convertor = ChoiceConvertor(choices)
        validators = ChoiceValidator(choices.values())

        return choices, cleaners, convertor, validators

    def refresh_screen(self):
        """
        Display the current page of the table (including any header or footer)

        :return: None
        """
        formatter = string.Formatter()

        # print header
        if self.header:
            print(formatter.vformat(self.header, None, self.action_dict))

        # print table
        if self.title is not None:
            print('{}'.format(self.title))

        print(self.table.get_string(fields=self.field_names))  # don't show action

        # print footer
        if self.footer:
            print(formatter.vformat(self.footer, None, self.action_dict))


    def _get_choice(self, table_choices, table_cleaners, table_convertor, table_validators, **options):
        """
        Internal function to get the input for the table choice.

        :param table_cleaners:
        :param table_convertor:
        :param table_validators:
        :param options:

        :return:  the table row for the choice picked
        """
        gi_options = {}
        gi_options['prompt'] = self.prompt
        gi_options['required'] = self.required
        gi_options['default'] = self.default_choice
        gi_options['default_str'] = self.default_str
        gi_options['commands'] = self.commands
        for k,v in options.items():
            gi_options[k] = v

        while True:
            try:
                self.refresh_screen()
                result = get_input(cleaners=table_cleaners, convertor=table_convertor, validators=table_validators, **gi_options)

                if result is None:
                    return None
                else:
                    return self._rows[result]
            except (FirstPageRequest):
                self.goto_home()
            except (LastPageRequest):
                self.goto_end()
            except (PageUpRequest):
                self.page_up()
            except (PageDownRequest):
                self.page_down()
            except (UpOneRowRequest):
                self.scroll_up_one_row()
            except (DownOneRowRequest):
                self.scroll_down_one_row()
            except (RefreshScreenInterrupt):
                table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input(force_refresh=True)
                self.show_rows(0)

    def get_table_choice(self, **options):
        """
        Pick a value from the table. This is the main method used to choose a value from a table.

        :param options: See below for details.

        :return: the result of performing the action (specified by the table or row) on the row. Returns None if no row picked.

        Options:

            - prompt: the prompt for choosing a table value.
            - required: requires an entry if True, exits the table on blank entry if False.
            - default: the default value to use.
            - default_str: An optional string to display for the defailt table selection.
            - commands: a dictionary of commands for the table. For each entry, the key is the command and the value the action
                        to take for the command. See GetInput and GetInputCommand for further details
        """
        table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
        self.show_rows(0)
        row = self._get_choice(table_choices, table_cleaners, table_convertor, table_validators, **options)

        if row is None:
            return None
        else:
            return self.do_action(row)


    def refresh_items(self, rows=None, add_exit=False, item_filter=None):
        """
        Refresh which rows of the table are enabled and shown. Used to update rows in the table. Adds tags if
        necessary. formatter is used so values can be substituted in format strings from action_dict using vformat.
        This is useful in case some TableItems have dynamic data. Can also be used by action to change table items.
        For instance a search action might filter for row entries using an item filter.

        :param rows: a list of rows to show. If None, will use all rows.
        :param add_exit: if TABLE_ADD_EXIT add am entry to exit, if TABLE_ADD_RETURN add an entry to return. Don't add
                            an entry if False (default).
        :param item_filter: an optional callable used to filter rows. See Table for details regarding item filters.

        :return: None
        """
        formatter = string.Formatter()

        if rows is None:
            use_rows = self._table_items
        elif isinstance(rows, TableItem):  # single item, not list
            use_rows = [rows]
        else:
            use_rows = rows

        self.table.clear_rows()
        self._rows = []

        table_idx = 1

        table_items = []
        for item in use_rows:
            table_items.append(item)

        if item_filter is None or item_filter is True:
            filtered_items = table_items
        elif callable(item_filter):
            filtered_items = []
            for item in table_items:
                # could set hidden and enabled directly, but it's easy to forget to return the tuple so warn the user...
                filter_result = item_filter(item, self.action_dict)
                try:
                    item.hidden, item.enabled = filter_result[0], filter_result[1]
                except TypeError:
                    raise RuntimeError('get_table: item_filter needs to return a tuple (hidden, enabled)')
                if item.hidden is False:
                    filtered_items.append(item)

        for item in filtered_items:
            if item.tag is None:
                tag = table_idx
            else:
                tag = item.tag

            item_values = []
            for v in item.values:
                if isstring(v):
                    try:
                        formatted_val = formatter.vformat(str(v), None, self.action_dict)
                    except ValueError: # a curly brace in the value causes a ValueError exception. Double it up to fix this.
                        v2 = str(v).replace('}', '}}').replace('{', '{{')
                        formatted_val = formatter.vformat(str(v2), None, self.action_dict)

                    item_values.append(formatted_val)
                else:
                    item_values.append(v)

            row_entry = TableItem(item_values, tag, item.action, item_data=item.item_data, hidden=item.hidden, enabled=item.enabled)

            self._rows.append(row_entry)
            table_idx += 1

        if add_exit not in (False, 'none') and self.add_exit not in (False, 'none'):
            num_values = 1
            if len(self._rows):
                num_values = len(self._rows[0].values)
            row_values = ['' for i in range(num_values)]
           
            if self.add_exit in (TABLE_ADD_EXIT, True):
                row_tag, row_action = 'exit', TABLE_ITEM_EXIT
            elif self.add_exit == TABLE_ADD_RETURN:
                row_tag, row_action = 'return', TABLE_ITEM_EXIT

            row_entry = TableItem(row_values, row_tag, row_action)

            self.table.add_row([row_entry.tag] + row_entry.values + [row_entry.action])
            self._rows.append(row_entry)

        # refresh table
        self.table.clear_rows()
        table_idx = 1
        for r in self._rows:
            if r.hidden is not True:
                self.table.add_row([r.tag] + r.values + [r.action])
            table_idx += 1

        if self.table.start > self.get_num_rows():
            # filtering can cause the table to not show any rows. If so, show last page of filtered table
            start_row = max(self.get_num_rows() - self.rows_per_page, 0)
            self.show_rows(start_row)


    def __call__(self, choice=None, action_dict=None):
        """
        Call the run method on the table.

        Note: choice and action_dict parameters are placeholders (ignored) so Tables can be used as action items
        in TableItems. This allows a Table instance to be used as a sub-menu by adding it as the action in a menu
        item.

        :param choice:
        :param action_dict:

        :return: the status from run.
        """
        return self.run()


    def run(self):
        """
        Continue to get input from the table until a blank row is returned, or a GetInputInterrupt is received. This is
        primarily used to use tables as menus. Choosing exit or return in a menu is the same as returning no row.

        :return: True if exited without an error, or False if a GetInputInterrupt was received.
        """
        table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
        self.show_rows(0)

        options = {'prompt': self.prompt}

        while True:
            try:
                choice = self._get_choice(table_choices, table_cleaners, table_convertor, table_validators, **options)
            except (GetInputInterrupt) as gii:
                print('\n{}\n'.format(gii))
                continue

            if choice is None:
                action - TABLE_ITEM_EXIT
            else:
                action = choice.action

            if action == TABLE_ITEM_EXIT:
                break
            elif action == TABLE_ITEM_RETURN:
                break
            elif action == TABLE_ITEM_DEFAULT:
                if callable(self.default_action):
                    try:
                        self.default_action(choice, self.action_dict)
                    except (GetInputInterrupt) as gii:
                        print('\n{}\n'.format(gii))
                        return False
                else:
                    print('Table:run: default_action not set for {}'.format(choice), file=sys.stderr)
            elif callable(action):
                try:
                    action(choice, self.action_dict)
                except (GetInputInterrupt) as gii:
                    print('\n{}\n'.format(gii))
                    continue
            else:
                print('Table.run - no action specified for {}'.format(choice), file=sys.stderr)

            if self.refresh:
                table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
                self.show_rows(self.table.start)

        return True


def get_table_input(table, **options):
    """
    Get input value from a table of values.

    :param table: a :class:`Table` instance
    :param options: all :class:`Table` options supported, see :class:`Table` documentation for details

    :return: the value from calling :func:`Table.get_table_choice` on the table
    :rtype: Any (dependent on the action function of the :class:`TableItem` selected)
    """
    return table.get_table_choice(**options)


def get_menu(choices, title=None, prompt=None, default_choice=None, add_exit=False, **options):
    """
    :param choices: the list of text strings to use for the menu items
    :param title: a title to use for the menu
    :param prompt: the prompt string used when asking the user for the menu selection
    :param default_choice: an optional default item to select
    :param add_exit: add an exit item if `True` or not if `False` (default)
    :param options: all :class:`Table` options supported, see :class:`Table` documentation for details.

    :return: the result of calling :func:`Table.get_table_choice` on the menu table. Will return the index (one based) of
        the choice selected, unless a different default action is provided in the options. Returns 'exit' if the input
        value is `None` or the menu was exited.
    :rtype: int or str (dependent on default action specified)

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

    # return the tag for the menu item unless the user set a specific default action.
    menu_options = dict(**options)

    if 'show_cols' not in options:
        menu_options['show_cols'] = False

    if 'show_border' not in options:
        menu_options['show_border'] = False

    if 'hrule' not in options:
        menu_options['hrules'] = RULE_NONE

    if 'vrule' not in options:
        menu_options['vrules'] = RULE_NONE

    if 'default_action' not in options:
        menu_options['default_action'] = return_tag_action

    if default_choice is not None:
        for i,mc in enumerate(menu_choices):
            try:
                if mc.tag is not None and mc.tag == default_choice:
                    default_idx = i+1
                elif mc.values[0] == default_choice:
                    default_idx = i+1
                elif mc.tag is None and i == int(default_choice):
                    default_idx = i+1
                break
            except ValueError:
                pass

    menu = Table(menu_choices, title=title, prompt=prompt, default_choice=default_idx, default_str=default_str,
                add_exit=add_exit, **menu_options)
    result = menu.get_table_choice()

    if result is None:
        return 'exit'

    # if add_exit and result.action=='exit':
    if add_exit!="none" and result=='exit':
        return 'exit'

    return result
