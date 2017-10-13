from __future__ import print_function

"""
get_menu - menu system for cooked_input

Len Wanger, 2017

TODO:

- Document and add to tutorial

- have dynamic menu function create MenuItems

- Examples/scenarios:
    - menus:
        X simple menu (numbered item built from list)
        X pick-once and exit
        X loop w/ pick until exit picked
        X action functions (with args/kwargs for context)
        X sub-menus
        X refresh option on menus to re-evaluate the MenuItems each pass through run (in case strings changed for dynamic items)
        X filter functions (i.e. only choices matching a role)
        X sub-menu with multiple parents
        X use lambda for actions
        - dynamic menu - from:
            X list
            X database
            - Pandas
        X test hidden commands. Test commands in header/footer
        - different display functions (i.e. function for displaying the table - silent_table for no display of menu or table)
        - set user profile - list users, add profile, edit profile
        - different borders
        - example runner
        - change Menus to tables - extend table to multiple columns with first as tag
        X Add hidden to MenuItem
        X Add disabled to MenuItem
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
    - curses ability - use get_string?
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
from collections import  namedtuple

import veryprettytable as pt
from cooked_input import get_input
from .cleaners import CapitalizationCleaner, StripCleaner, ChoiceCleaner
from .convertors import ChoiceConvertor
from .validators import RangeValidator


MENU_DEFAULT_ACTION = 'default'
MENU_ACTION_EXIT = 'exit'
MENU_ACTION_RETURN = 'return'

MENU_ADD_EXIT = 'exit'
MENU_ADD_RETURN = 'return'


class MenuItem(object):
    def __init__(self, text, tag=None, action=MENU_DEFAULT_ACTION, item_data=None, hidden=False, enabled=True):
        """
        MenuItem is used to represent individual menu items (choices) in the Menu class.

        :param text: the text description to be used for the item in the printed menu
        :param tag:  a value that can be used to choose the item. If None, a default tag will be assigned by the Menu
        :param action:  the action to take when the item is selected
        :param item_data:  a dictionary containing data for the menu item. Used for item filters
        :param hidden:  menu item will not be shown if True (but will still be selectable), the menu item is shown if False (default)
        :param enabled:  menu item is shown and selectable if True (default), shown and not selectable if False

        MenuItem actions:

        +---------------------+--------------------------------------------------------------------------+
        | value               | action                                                                   |
        +---------------------+--------------------------------------------------------------------------+
        | MENU_DEFAULT_ACTION |  use default method to handle the menu item (e.g. call                   |
        |                     |  default_action handler function)                                        |
        +---------------------+--------------------------------------------------------------------------+
        | MENU_ACTION_EXIT    |  the menu item should exit the menu                                      |
        +---------------------+--------------------------------------------------------------------------+

        """
        self.text = text
        self.tag = tag
        self.action = action
        self.item_data = item_data
        self.hidden = hidden
        self.enabled = enabled

    def __repr__(self):
        return 'MenuItem(text={}, tag={}, action={}, item_data={}, hidden={}, enabled={})'.format(self.text, self.tag,
                        self.action, self.item_data, self.hidden, self.enabled)


#class DynamicMenuItem(object):
class DynamicMenuItem(MenuItem):
    def __init__(self, query, menu_item_factory, item_data=None):
        self.query = query
        self.menu_item_factory = menu_item_factory
        self. item_data = item_data
        # no call to super... sub-class is so isinstance works to detect subclass.

    def __repr__(self):
        return 'DynamicMenuItem(query={}, make_menu_entry={}, item_data={})'.format(self.query, self.menu_item_factory, self.item_data)

    def __call__(self, *args, **kwargs):
        mis = []

        for i, row in enumerate(self.query):
            mi = self.menu_item_factory(i+1, row, self.item_data)
            mis.append(mi)

        return mis


class Menu(object):
    def __init__(self, rows=(), title=None, prompt=None, default_choice=None, default_str=None, default_action=None, **options):
        """

        :param rows:
        :param title:
        :param prompt:
        :param default_choice:
        :param default_str:
        :param default_action:
        :param options: see below for a list of valid options

        Options:

        required            requires an entry if True, exits the menu on blank entry if False

        add_exit            automatically adds a MenuItem to exit the menu (MENU_ADD_EXIT - default) or return to the
                            parent menu (MENU_ADD_RETURN), or not to add a MenuItem at all (False)
        action_dict         a dictionary of values to pass to action functions. Used to provide context to the action
        case_sensitive      whether choosing menu items should be case sensitive (True) or not (False - default)
        item_filter         a function used to determine which menu items to display. An item is display if the function returns True for the item.
                                All items are displayed if item_filter is None (default)
        refresh             refresh menu items each time the menu is shown (True - default), or just when created (False). Useful for dynamic menus
        item_filter              a function used to filter menu items. MenuItem is shown if returns True, and not if False
        header              a format string to print before the table, can use any value from action_dict as well as pagination information
        footer              a format string to print after the table, can use any values from action_dict as well as pagination information
        """
        try:
            self.required = options['required']
        except KeyError:
            self.required = True

        try:
            add_exit = options['add_exit']
            if add_exit in { False, MENU_ADD_EXIT, MENU_ADD_RETURN }:
                self.add_exit = add_exit
            else:
                print('Menu:__init__: ')
                raise RuntimeError('Menu: unexpected value for add_exit option ({})'.format(add_exit))
        except KeyError:
            self.add_exit = MENU_ADD_EXIT

        try:
            self.action_args = options['action_args']
        except KeyError:
            self.action_args = []

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
            self.prompt = 'Choose a menu item'
        else:
            self.prompt = prompt

        self.title = title
        self.default_choice = default_choice
        self.default_str= default_str
        self.default_action = default_action
        self._menu_items = rows             # the original, raw menu items for the menu
        self._rows = []                     # the expanded, refreshed menu items for the menu used to create the pretty table
        self.tbl = pt.VeryPrettyTable()     # the pretty table to display

        self.tbl.field_names = "tag text action".split()
        self.tbl.set_style(pt.PLAIN_COLUMNS)
        self.tbl.border = False
        self.tbl.header = False
        self.tbl.align = 'l'
        self.tbl.align['tag'] = 'r'
        # self.tbl.left_padding_width = 2

        if self.refresh is False:
            self.refresh_items(rows=rows, add_exit=True, item_filter=self.item_filter)

    def __repr__(self):
        return 'Menu(rows={}, title={}, prompt={}, default_choice={}, action_dict={})'.format(self._menu_items, self.title,
                    self.prompt, self.default_choice, self.action_dict)

    def get_numchoices(self):
        return len(self._rows)

    def get_row(self, tag):
        for row in self._rows:
            if row.tag == tag:
                return row
        raise ValueError('Menu.get_row: tag ({}) not in the menu'.format(tag))

    def get_action(self, tag):
        for row in self._rows:
            if row.tag == tag:
                return row.action
        raise ValueError('Menu.get_action: tag ({}) not in the menu'.format(tag))
    

    def do_action(self, tag):
        row = self.get_row(tag)
        action = row.action
        if callable(action):
            action(tag, self.action_dict, row.item_data)
        elif action == 'default' and self.default_action is not None:
            self.default_action(tag, self.action_dict, row.item_data)

    def _prep_get_input(self):
        if self.refresh:
            self.refresh_items(self._menu_items, self.add_exit, self.item_filter)

        if self.case_sensitive:
            choices = {str(item.tag): i for i, item in enumerate(self._rows) if item.enabled is True}
        else:
            choices = {str(item.tag).lower(): i for i, item in enumerate(self._rows) if item.enabled is True}

        cleaners = [StripCleaner()]
        if not self.case_sensitive:
            cleaners.append(CapitalizationCleaner('lower'))
        cleaners.append(ChoiceCleaner(choices))

        convertor = ChoiceConvertor(choices)
        validators = RangeValidator(min_val=0, max_val=max(choices.values()))
        return choices, cleaners, convertor, validators

    def _get_choice(self, menu_choices, menu_cleaners, menu_convertor, menu_validators):
        formatter = string.Formatter()

        # print header
        if self.header:
            print( formatter.vformat(self.header, None, self.action_dict) )

        # print table
        if self.title is not None:
            print('{}'.format(self.title))
        print(self.tbl.get_string(fields=['tag', 'text']))  # don't show action

        # print footer
        if self.footer:
            print( formatter.vformat(self.footer, None, self.action_dict) )

        result = get_input(prompt=self.prompt, cleaners=menu_cleaners, convertor=menu_convertor,
                           validators=menu_validators, default=self.default_choice, default_str=self.default_str, required=self.required)

        if result is None:
            return None
        else:
            return self._rows[result]

    def get_menu_choice(self):
        menu_choices, menu_cleaners, menu_convertor, menu_validators = self._prep_get_input()
        row = self._get_choice(menu_choices, menu_cleaners, menu_convertor, menu_validators)

        if row is None:
            return 'exit'
        else:
            return row.tag

    def refresh_items(self, rows=None, add_exit=False, item_filter=None):
        # Used to update rows in the table. Adds tags if necessary. formatter is used so
        # values can be substituted in format strings from action_dict using vformat.
        formatter = string.Formatter()

        if rows is None:
            use_rows = self._menu_items
        elif isinstance(rows, MenuItem):  # single item, not list
            use_rows = [rows]
        else:
            use_rows = rows

        self.tbl.clear_rows()
        self._rows = []

        menu_idx = 1

        menu_items = []
        for item in use_rows:
            if isinstance(item, DynamicMenuItem):  # expand dynamic rows
                menu_items.extend(item())
            else:
                menu_items.append(item)

        if item_filter is None or item_filter is True:
            filtered_items = menu_items
        elif callable(item_filter):
            filtered_items = []
            for item in menu_items:
                if  item_filter(item, self.action_dict):
                    filtered_items.append(item)

        for item in filtered_items:
            if item.tag is None:
                tag_str = '{:3}'.format(menu_idx)
                tag = menu_idx
            else:
                tag = tag_str = item.tag

            row_entry = MenuItem(formatter.vformat(item.text, None, self.action_dict), tag, item.action,
                                   item_data=item.item_data, hidden=item.hidden, enabled=item.enabled)

            if item.hidden is not True:
                self.tbl.add_row([tag_str, formatter.vformat(item.text, None, self.action_dict), item.action])

            self._rows.append(row_entry)
            menu_idx += 1

        if add_exit and self.add_exit:
            if self.add_exit == MENU_ADD_EXIT:
                row_entry = MenuItem('exit', 'exit', MENU_ACTION_EXIT)
            if self.add_exit == MENU_ADD_RETURN:
                row_entry = MenuItem('return', 'return', MENU_ACTION_EXIT)

            self.tbl.add_row([row_entry.tag, row_entry.text, row_entry.action])
            self._rows.append(row_entry)


    def __call__(self, tag=None, args=[], kwargs={}):
        """
        This makes Menus convenient by making them callable. To call the run method on a menu just call the
        menu like a function: (i.e. my_menu()). The reason it takes takes, args, and kwargs is so it can be
        used for submenus by putting the menu as the action for the MenuItem.

        :param tag: tag the menu was called with (used for submenus)
        :param args: arg list the menu was called with (used for submenus)
        :param kwargs: keyword arg dictionary the menu was called with (used for submenus)
        :return: the status from run.
        """
        return self.run()

    def run(self):
        menu_choices, menu_cleaners, menu_convertor, menu_validators = self._prep_get_input()

        while True:
            choice = self._get_choice(menu_choices, menu_cleaners, menu_convertor, menu_validators)

            if choice is None:
                action - MENU_ACTION_EXIT
            else:
                action = choice.action

            if action == MENU_ACTION_EXIT:
                break
            elif action == MENU_ACTION_RETURN:
                break
            elif action == MENU_DEFAULT_ACTION:
                if callable(self.default_action):
                    self.default_action(choice.tag, self.action_dict, choice.item_data)
                else:
                    print('Menu:run: default_action not set for {}'.format(choice), file=sys.stderr)
            elif callable(action):
                action(choice.tag, self.action_dict, choice.item_data)
            else:
                print('Menu.run - no action specified for {}'.format(choice), file=sys.stderr)

            if self.refresh:
                menu_choices, menu_cleaners, menu_convertor, menu_validators = self._prep_get_input()

        return True


def get_menu(choices, title=None, prompt=None, default_choice='', add_exit=False, **kwargs):
    menu_choices = [MenuItem(choice) for choice in choices]
    default_str = default_choice
    default_idx = None

    for i,mc in enumerate(menu_choices):
        if mc.text == default_choice:
            default_idx = i+1
            break

    menu = Menu(menu_choices, title=title, prompt=prompt, default_choice=default_idx, default_str=default_str,
                add_exit=add_exit, **kwargs)
    result = menu.get_menu_choice()

    if result is None:
        return 'exit'

    if add_exit and result=='exit':
        return result

    return menu_choices[result-1].text
