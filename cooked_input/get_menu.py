"""
get_menu - menu system for cooked_input

Len Wanger, 2017

TODO:
    - When settles down, add calls to __init__.py

- Examples/scenarios:
    - menus:
        - example runner
        X simple menu (numbered item built from list)
        - action functions (with args/kwargs for context)
        - sub-menus
        - different borders
        - sub-menu with multiple parents
        - pick-once and quit
        - loop w/ pick until quit picked
        - dynamic menu - from: list, pretty-table, database, Pandas
        - different display functions (i.e. function for displaying the table - silent_table for no display of menu or table)
        - filter functions (i.e. only choices matching a role)
        - set user profile - list users, add profile, edit profile
        - use lambda for actions
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

from future.utils import raise_from
import sys
from collections import namedtuple
import veryprettytable as pt
from cooked_input import get_input, Convertor, Validator, CapitalizationCleaner, StripCleaner, ChoiceCleaner, ChoiceValidator, RangeValidator
from cooked_input.input_utils import put_in_a_list
from cooked_input import ConvertorError


MenuChoice = namedtuple("MenuChoice", "tag text action")

MENU_DEFAULT_ACTION = 'default'
MENU_ACTION_QUIT = 'quit'


class TableRowConvertor(Convertor):
    """
    convert the cleaned input to the integer row of a table
    """
    def __init__(self, choices=(), value_error_str='a valid row number', **kwargs):
        choices_list = put_in_a_list(choices)
        self._choices = {v: i for i,v in enumerate(choices_list)}
        super(TableRowConvertor, self).__init__(value_error_str, **kwargs)

    def __call__(self, value, error_callback, convertor_fmt_str):
        result = None
        try:
            result = self._choices[value]
        except (KeyError) as ve:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise_from(ConvertorError(str(ve)), ve)

        return result

    def __repr__(self):
        return 'TableRowConvertor(choices={}, value_error_str={})'.format(self._choices, self.value_error_str)


class CIMenu(object):
    def __init__(self, rows=(), default_action=None, **kwargs):
        try:
            self.add_quit = kwargs['add_quit']
        except KeyError:
            self.add_quit = True

        try:
            self.action_args = kwargs['action_args']
        except KeyError:
            self.action_args = []

        try:
            self.action_kwargs = kwargs['action_kwargs']
        except KeyError:
            self.action_kwargs = {}

        self.default_action = default_action
        self._rows = []
        self.tbl = pt.VeryPrettyTable()

        self.tbl.field_names = "tag text action".split()
        self.tbl.set_style(pt.PLAIN_COLUMNS)
        self.tbl.border = False
        self.tbl.header = False
        self.tbl.align = 'l'
        self.tbl.align['tag'] = 'r'
        self.tbl.left_padding_width = 2

        for i, v in enumerate(rows):
            if v.tag is None:
                r = ['{:3}'.format(i+1), v.text, v.action]
                r2 = MenuChoice(i+1, v.text, v.action)
            else:
                r = [v.tag, v.text, v.action]
                r2 = v

            self.tbl.add_row(r)
            self._rows.append(r2)

        if self.add_quit:
            r = MenuChoice('quit', 'quit', MENU_ACTION_QUIT)
            self.tbl.add_row([r.tag, r.text, r.action])
            self._rows.append(r)


    def get_numchoices(self):
        return len(self._rows)


    def get_action(self, tag):
        for row in self._rows:
            if row.tag == tag:
                return row.action
        raise ValueError('CIMenu.get_action: tag ({}) not in the menu'.format(tag))

    def _prep_get_input(self):
        choices = tuple(c[0] for c in self._rows)
        cleaners = [StripCleaner(), CapitalizationCleaner('lower'), ChoiceCleaner(choices)]
        convertor = TableRowConvertor(choices)
        validators = RangeValidator(min_val=0, max_val=len(choices))
        return choices, cleaners, convertor, validators

    def _get_choice(self, menu_choices, menu_cleaners, menu_convertor, menu_validators):
        print('Menu:\n')
        print(self.tbl.get_string(fields=['tag', 'text']))  # don't show action
        result = get_input(prompt='What would you like to do?: ', cleaners=menu_cleaners, convertor=menu_convertor,
                           validators=menu_validators)
        # print('result={}, action={}'.format(result, self.get_action(result-1)))
        row = self._rows[result]
        return row

    def get_menu_choice(self):
        menu_choices, menu_cleaners, menu_convertor, menu_validators = self._prep_get_input()
        row = self._get_choice(menu_choices, menu_cleaners, menu_convertor, menu_validators)
        return row.tag

    def run(self):
        menu_choices, menu_cleaners, menu_convertor, menu_validators = self._prep_get_input()

        while True:
            choice = self._get_choice(menu_choices, menu_cleaners, menu_convertor, menu_validators)
            action = choice.action

            if action == MENU_ACTION_QUIT:
                break
            elif action == MENU_DEFAULT_ACTION:
                self.default_action(choice.tag, self.action_args, self.action_kwargs)
            elif callable(action):
                action(choice.tag, self.action_args, self.action_kwargs)
            else:
                print('CIMenu.run - no action specified for tag ({})'.format(choice.tag), file=sys.stderr)
        return True


### test ####
def default_action(tag, *args, **kwargs):
    print('called default_action, tag={}, args={} kwargs={}'.format(tag, args, kwargs))
    return True

def action_1(tag, *args, **kwargs):
    print('called action_1')
    return True


def simple_menu():
    menu_choices = [
        MenuChoice(None, "Choice 1", None),
        MenuChoice(2, "Choice 2", MENU_DEFAULT_ACTION),
        MenuChoice('foo', "Do Foo", MENU_DEFAULT_ACTION),
        MenuChoice('bar', "Do Bar (action_1)", action_1),
        MenuChoice('stop', "STOP the menu!", MENU_ACTION_QUIT),
    ]

    print('\nget_menu_choice - add_quit=True')
    menu = CIMenu(menu_choices[:-1])
    choice = menu.get_menu_choice()
    print('choice={}, action={}'.format(choice, menu.get_action(choice)))

    print('\nget_menu_choice - add_quit=False (no exit!)')
    menu = CIMenu(menu_choices[:-1], add_quit=False)
    choice = menu.get_menu_choice()
    print('choice={}, action={}'.format(choice, menu.get_action(choice)))

    print('\nget_menu_choice - add_quit=False')
    menu = CIMenu(menu_choices, default_action=default_action, add_quit=False)
    choice = menu.get_menu_choice()
    print('choice={}, action={}'.format(choice, menu.get_action(choice)))

    print('\nmenu.run - add_quit=False')
    menu.run()
    print('done')


if __name__ == '__main__':
    simple_menu()