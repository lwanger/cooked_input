from __future__ import print_function

"""
get_menu - menu system for cooked_input

Len Wanger, 2017

TODO:

    - navigation keys
    - Document and add to tutorial

- Examples/scenarios:
    - menus:
        - different display functions (i.e. function for displaying the table - silent_table for no display of menu or table)
        - set user profile - list users, add profile, edit profile
        - different borders
        - example runner
        - change Menus to tables - extend table to multiple columns with first as tag
        - How to deal with non unique tags? Unique option and keep set of tags? Or pick first, or pick from current paginated page
        X Header and footer to print. So can have commands listed per page as hidden menu items (e.g. Search or filter)
        - Dynamic function - for long tables, lookup entered value instead of showing as rows. Maybe lazy evaluation? A lookup cleaner?
"""

"""
TODO:
    - Look at veryprettytable? https://github.com/smeggingsmegger/VeryPrettyTable/blob/master/veryprettytable.py
    - Look at: https://github.com/moul/prettytable-extras
        adds color_styles: 'bold','italic','underline','inverse', white,gray,black,blue,cyan,green,magenta,red,yellow
        new PrettyTable kwarg options - auto_width, header_color
    - port prettytable-extras to veryprettytable?
    - add color for title and header
    - add setting fore and back colors on rows? (int or slice?)
    - curses ability - use get_string? use prompt toolkit?
    - pagination - add paginator? - paginate in veryprettytable isn't quite right... need like flask paginate
        Pagination()
            __init__(page, per_page, total_count)   <-- can add search (and search col?)
                cur_page
                found   - when searching
                per_page
                search - None or value? or callable function (key)
                total - total records for pagination
                display_msg - fmt string for all these things (gets variables for cur_page, found, total_pages, etc.)
                search_msg
            has_prev()
            has_next()
            iter_pages()
            render(page_num='first'|'last'|'current'|'next'|'last'|#) - renders with stop/end and navigation (page x of y) or 'found' with search
navigation buttons (selected line and up/down, pageup/pagedown, home,end
"""


import sys
import string
import logging

import veryprettytable as pt

from cooked_input import get_input
from cooked_input import GetInputInterrupt, RefreshScreenInterrupt
from .input_utils import put_in_a_list, isstring
from .cleaners import CapitalizationCleaner, StripCleaner, ChoiceCleaner
from .convertors import ChoiceConvertor
from .validators import ChoiceValidator


TABLE_DEFAULT_ACTION = 'default'
TABLE_ACTION_EXIT = 'exit'
TABLE_ACTION_RETURN = 'return'

TABLE_ADD_EXIT = 'exit'
TABLE_ADD_RETURN = 'return'
TABLE_ADD_NONE = 'none'


def return_table_item_action(row, action_dict):
    """
    Default action function for Tables. This function returns the whole row of data.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data for the selected row of the table.
    """
    return row


def return_row_action(row, action_dict):
    """
    Default action function for Tables. This function returns the whole row of data.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data for the selected row of the table.
    """
    return row.values


def return_tag_action(row, action_dict):
    """
    Default action function for menus. This function returns the tag for the
    row of data.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data for the selected row of the table.
    """
    return row.tag

def return_first_col_action(row, action_dict):
    """
    Default action function for menus. This function returns the first data column value for the
    row of data.

    :param row: the data associated with the selected row
    :param action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data for the selected row of the table.
    """
    return row.values[0]


class TableItem(object):
    def __init__(self, col_values, tag=None, action=TABLE_DEFAULT_ACTION, item_data=None, hidden=False, enabled=True):
        """
        # TODO - flesh out documentation - for instance parameters to action calls

        TableItem is used to represent individual rows in a table. Can also be used for menu items.

        :param col_values: A list of values the row's columns
        :param tag:  a value that can be used to choose the item. If None, a default tag will be assigned by the Table
            The tag is often an integer of the row number, a database ID, or a textual tag.
        :param action:  the action to take when the item is selected. By default the tag value is returned.
        :param item_data:  a dictionary containing data for the table row. Can be used for database ID's. Also
            used for item filters
        :param hidden:  Table row will not be shown if True (but will still be selectable), the table row is shown
            if False (default). Useful for filtering tables
        :param enabled:  Table row is shown and selectable if True (default), shown and not selectable if False

        TableItem actions:

        +----------------------+--------------------------------------------------------------------------+
        | value                | action                                                                   |
        +----------------------+--------------------------------------------------------------------------+
        | TABLE_DEFAULT_ACTION |  use default method to handle the table item (e.g. call                  |
        |                      |  default_action handler function)                                        |
        +----------------------+--------------------------------------------------------------------------+
        | TABLE_ACTION_EXIT    |  selecting the table row should exit (ie exit the menu)                  |
        +----------------------+--------------------------------------------------------------------------+
        | TABLE_ACTION_RETURN  |  selecting the table row should return (ie return from the menu)         |
        +----------------------+--------------------------------------------------------------------------+

        """
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
    # TODO - document, including actions

    def __init__(self, rows, col_names=None, title=None, prompt=None, default_choice=None, default_str=None,
                 default_action=None, rows_per_page=20, **options):
        """

        :param rows:
        :param col_names:
        :param title:
        :param prompt:
        :param default_choice:
        :param default_str:
        :param default_action:
        :param rows_per_page:
        :param options: see below for a list of valid options

        Options:

        required            requires an entry if True, exits the menu on blank entry if False
        add_exit            automatically adds a MenuItem to exit the menu (MENU_ADD_EXIT - default) or return to the
                            parent menu (MENU_ADD_RETURN), or not to add a MenuItem at all (False)
        action_dict         a dictionary of values to pass to action functions. Used to provide context to the action
        case_sensitive      whether choosing menu items should be case sensitive (True) or not (False - default)
        item_filter         a function used to determine which menu items to display. An item is display if the function returns True for the item.
                                All items are displayed if item_filter is None (default) -- TODO - returns a tuple of (hidden, enabled)
        refresh             refresh menu items each time the menu is shown (True - default), or just when created (False). Useful for dynamic menus
        header              a format string to print before the table, can use any value from action_dict as well as pagination information
        footer              a format string to print after the table, can use any values from action_dict as well as pagination information
        """
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
            self.add_exit = TABLE_ADD_EXIT

        try:
            self.action_dict = options['action_dict']
        except KeyError:
            self.action_dict = {}

        try:
            self.case_sensitive = options['case_sensitive']
        except KeyError:
            self.case_sensitive = False

        try:
            self.refresh = options['refresh']
        except KeyError:
            self.refresh = True

        try:
            self.item_filter = options['item_filter']
        except KeyError:
            self.item_filter = None

        try:
            self.header = options['header']
        except KeyError:
            self.header = None

        try:
            self.footer = options['footer']
        except KeyError:
            self.footer = None

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
        elif default_action is None or default_action == 'first_value':
            self.default_action = return_first_col_action
        elif default_action == 'row':
            self.default_action = return_row_action
        elif default_action == 'table_item':
            self.default_action = return_table_item_action
        else:
            self.default_action = default_action

        self.rows_per_page = rows_per_page
        self._table_items = put_in_a_list(rows)             # the original, raw table items for the table
        self._rows = []                     # the expanded, refreshed table items for the table used to create the pretty table
        self.table = pt.VeryPrettyTable()     # the pretty table to display

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

        self.table.set_style(pt.PLAIN_COLUMNS)
        self.table.border = False
        self.table.header = False
        self.table.align = 'l'
        self.table.align['tag'] = 'r'
        # self.tbl.left_padding_width = 2

        if self.refresh is False:   # set up rows to start as won't be refreshed each time called
            self.refresh_items(rows=rows, add_exit=True, item_filter=self.item_filter)
        # self.refresh_items(rows=rows, add_exit=True, item_filter=self.item_filter)

        self.show_rows(0)


    def __repr__(self):
        return 'Table(rows={}, col_name={}, title={}, prompt={}, default_choice={}, action_dict={})'.format(self._table_items,
                                            self.field_names, self.title, self.prompt, self.default_choice, self.action_dict)

    def get_num_rows(self):
        return len(self._rows)

    def get_row(self, tag):
        for row in self._rows:
            if row.tag == tag:
                return row
        raise ValueError('Table.get_row: tag ({}) not in the table'.format(tag))

    def get_action(self, tag):
        row = self.get_row(tag)
        return row.action

    def do_action(self, row):
        action = row.action
        if callable(action):
            return action(row, self.action_dict)
        elif action == 'default' and self.default_action is not None:
            return self.default_action(row, self.action_dict) # TODO - passing row now -- item_data available from row
        else:
            return row

    def show_rows(self, start_row):
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


    def page_up(self, buffer=None):
        # page up for the table
        self.show_rows(self.table.start - self.rows_per_page)
        print(self.table.get_string())

    def page_down(self, buffer=None):
        self.show_rows(self.table.start + self.rows_per_page)
        print(self.table.get_string())

    def goto_home(self, buffer=None):
        # page up for the table
        self.show_rows(0)
        print(self.table.get_string())

    def goto_end(self, buffer=None):
        # page up for the table
        self.show_rows(self.get_num_rows() - self.rows_per_page)
        print(self.table.get_string())

    def scroll_up_one_row(self, buffer=None):
        # go up one row
        self.show_rows(self.table.start + 1)
        print(self.table.get_string())

    def scroll_down_one_row(self, buffer=None):
        # go down one row
        self.show_rows(self.table.start - 1)
        print(self.table.get_string())


    def _prep_get_input(self):
        if self.refresh:
            self.refresh_items(self._table_items, self.add_exit, self.item_filter)
        if len(self._rows) == 0:
            raise RuntimeError('get_menu::_prep_get_input: Table has no rows of data ({}).'.format(self))

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
        gi_options = {}
        gi_options['prompt'] = self.prompt
        gi_options['required'] = self.required
        gi_options['default'] = self.default_choice
        gi_options['default_str'] = self.default_str
        for k,v in options.items():
            gi_options[k] = v

        self.refresh_screen()
        result = get_input(cleaners=table_cleaners, convertor=table_convertor, validators=table_validators, **gi_options)

        if result is None:
            return None
        else:
            return self._rows[result]

    def get_table_choice(self, do_action=True, **options):
        # TODO - document - get the choice from the table - does not run the action...
        # TODO - can raise GetInputInterrupt... handle here or not?

        table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
        self.show_rows(0)
        row = self._get_choice(table_choices, table_cleaners, table_convertor, table_validators, **options)

        if row is None:
            # return 'exit'
            return None
        else:
            return self.do_action(row)

    def refresh_items(self, rows=None, add_exit=False, item_filter=None):
        # Used to update rows in the table. Adds tags if necessary. formatter is used so
        # values can be substituted in format strings from action_dict using vformat.
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
                    raise RuntimeError('get_menu: item_filter needs to return a tuple (hidden, enabled)')
                if item.hidden is False:
                    filtered_items.append(item)

        for item in filtered_items:
            if item.tag is None:
                # tag_str = '{:3}'.format(table_idx)
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

            # if item.hidden is not True:
            #     self.table.add_row([tag_str] + item_values + [item.action])

            self._rows.append(row_entry)
            table_idx += 1

        if add_exit and self.add_exit:
            num_values = 1
            if len(self._rows):
                num_values = len(self._rows[0].values)
            row_values = ['' for i in range(num_values)]
           
            if self.add_exit in (TABLE_ADD_EXIT, True):
                row_tag, row_action = 'exit', TABLE_ACTION_EXIT
            elif self.add_exit == TABLE_ADD_RETURN:
                row_tag, row_action = 'return', TABLE_ACTION_EXIT

            row_entry = TableItem(row_values, row_tag, row_action)

            self.table.add_row([row_entry.tag] + row_entry.values + [row_entry.action])
            self._rows.append(row_entry)

        # refresh table
        self.table.clear_rows()
        table_idx = 1
        for r in self._rows:
            if r.hidden is not True:
                # self.table.add_row([tag_str] + item_values + [item.action])
                self.table.add_row([r.tag] + r.values + [r.action])
            table_idx += 1

        if self.table.start > self.get_num_rows():
            # filtering can cause the table to not show any rows. If so, show last page of filtered table
            start_row = max(self.get_num_rows() - self.rows_per_page, 0)
            self.show_rows(start_row)


    def __call__(self, tag=None, action_dict={}, item_data={}):
        """
        This makes tables convenient by making them callable. To call the run method on a table just call the
        table like a function: (i.e. my_table()). The reason it takes takes, args, and kwargs is so it can be
        used for submenus by putting the menu as the action for the TableItem.

        :param tag: tag the table was called with (used for submenus)
        :param args: arg list the table was called with (used for submenus)
        :param kwargs: keyword arg dictionary the table was called with (used for submenus)
        :return: the status from run.
        """
        return self.run()

    def run(self):
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
                action - TABLE_ACTION_EXIT
            else:
                action = choice.action

            if action == TABLE_ACTION_EXIT:
                break
            elif action == TABLE_ACTION_RETURN:
                break
            elif action == TABLE_DEFAULT_ACTION:
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


def get_menu(choices, title=None, prompt=None, default_choice=None, add_exit=False, **kwargs):
    # TODO - document!
    menu_choices = [TableItem(choice) for choice in choices]
    default_str = default_choice
    default_idx = None

    # return the tag for the menu item unless the user set a specific default action.
    menu_options = dict(**kwargs)

    if 'default_action' not in kwargs:
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

    if add_exit and result=='exit':
        return result

    return result
