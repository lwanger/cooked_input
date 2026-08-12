"""
cooked input example of using table input to pick from a menu.

TODO:

- simplify examples

Len Wanger, 2017
"""

# from collections import namedtuple

import sqlite3
from contextlib import closing

from cooked_input import get_menu, get_string, get_int, get_list, validate, Validator, ChoiceValidator
from cooked_input import GetInput
from cooked_input import silent_error
from cooked_input import Table
from cooked_input import TableItem, TableStyle, TABLE_ITEM_DEFAULT, TABLE_ITEM_EXIT, TABLE_ITEM_RETURN, TABLE_ADD_RETURN, TABLE_ADD_EXIT
from cooked_input import TABLE_RETURN_FIRST_VAL, RULE_NONE, RULE_ALL


# TODO - actions are wrong!

def test_get_menu_1():
    choices = ['red', 'blue', 'green']
    print('test_get_menu:\n')
    print('simplest case:\n')
    result = get_menu(choices)
    print('result={}'.format(result))


def test_get_menu_2():
    choices = ['red', 'blue', 'green']
    print('\nwith options...\n')
    prompt_str = 'Enter a menu choice'
    result = get_menu(choices, title='My Menu', prompt=prompt_str, default_choice='red',  add_exit=TABLE_ADD_EXIT,
                      case_sensitive=True, default_action=TABLE_RETURN_FIRST_VAL)
    print('result={}'.format(result))


def default_action(row, kwargs):
    print('called default_action, tag={}, row={}, kwargs={}'.format(row.tag, row, kwargs))
    return True


def action_1(row, action_dict):
    print('called action_1, tag={}, row={}, action_dict={}'.format(row.tag, row, action_dict))
    return True


def show_choice(menu, choice):
    print('choice={}'.format(choice))


def test_action_table():
    menu_choices = [
        TableItem("Choice 1 - no specified tag, no specified action", None, None),
        TableItem("Choice 2 - default action", 2, TABLE_ITEM_DEFAULT),
        TableItem("Choice 3 - text tag, lambda action", 'foo', lambda row,kwargs: print('lambda action: row={}, kwargs={}'.format(row,kwargs))),
        TableItem("Choice 4 - text tag, action handler function specified", 'bar', action_1),
        TableItem("STOP the menu!", 'stop', TABLE_ITEM_EXIT),
    ]


    print('\nget_table_choice - add_exit=True\n')
    use_style = TableStyle(show_cols=False, show_border=False, vrules=RULE_NONE)
    menu = Table(menu_choices[:-1], add_exit=True, tag_str="", style=use_style)
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nget_table_choice - add_exit=False (no exit!), case_sensitive=True, with title, no columns\n')
    use_style = TableStyle(show_cols=False, show_border=True, vrules=RULE_NONE)
    menu = Table(menu_choices[:-1], title='My Menu:', add_exit=False, case_sensitive=True, style=use_style)
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nget_table_choice - add_exit=False, w/ prompt, default="stop", hrule=ALL, vrule=NONE\n')
    use_style = TableStyle(show_cols=False, hrules=RULE_ALL, vrules=RULE_NONE)
    menu = Table(menu_choices, prompt='Choose or die!', default_choice='stop', default_action=default_action,
                 add_exit=False, style=use_style)
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nget_table_choice - add_exit=False, w/ prompt, default="stop", no columns, no border\n')
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    # Fixing: this passed show_border/show_cols to Table, which has no such options -- they are
    # TableStyle fields. They landed in the **options bag and were silently dropped, so this demo
    # drew its usual border and column headings while announcing it had neither. use_style, built
    # on the line above with exactly those two settings, was never passed at all.
    menu = Table(menu_choices, prompt='Choose or die!', default_choice='stop', default_action=default_action,
                 add_exit=False, style=use_style)
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nmenu.run - add_exit=True\n')
    menu.add_exit = True
    menu.run()
    print('done')


def sub_menu_action(row, action_dict):
    print('sub_menu2: row={}, action_dict={}'.format(row, action_dict))

    sub_menu_choices = [
        TableItem("sub menu 2: Choice 1", 1, TABLE_ITEM_DEFAULT),
        TableItem("sub menu 2: Choice 2", 2, TABLE_ITEM_DEFAULT),
    ]
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    sub_menu = Table(sub_menu_choices, title="Sub-Menu 2", add_exit=TABLE_ADD_RETURN, style=use_style)
    sub_menu.run()


def test_sub_table():
    sub_menu_1_items = [
        TableItem("sub menu 1: Choice 1", 1, TABLE_ITEM_DEFAULT),
        TableItem("sub menu 1: Choice 2", 2, TABLE_ITEM_DEFAULT),
    ]
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    sub_menu_1 = Table(sub_menu_1_items, title="Sub-Menu 2", add_exit=TABLE_ADD_RETURN, style=use_style)

    # call submenus two different ways. First by using it as a callable, which calls run on the sub_menu, and second
    # with an explicit action handler
    menu_choices = [
        TableItem("Choice 1", None, TABLE_ITEM_DEFAULT),
        TableItem("sub_menu 1", None, sub_menu_1),
        TableItem("sub_menu 2", None, sub_menu_action),
    ]

    print('\nmenu.run - with sub-menu\n')
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    menu = Table(menu_choices, add_exit=True, style=use_style)
    menu.run()
    print('done')


def change_kwargs(row, action_dict):
    # Change the action_dict values...
    tag = row.tag
    if tag == 1:
        action_dict['first'] = 'Ron'
        action_dict['last'] = 'McGee'
    elif tag == 2:
        action_dict['first'] = 'Len'
        action_dict['last'] = 'Wanger'

    print(f'action_dict={action_dict}')
    return action_dict


def test_args_table():
    print('test sending args and kwargs to menus:\n')

    menu_choices = [
        TableItem("Change kwargs to Ron McGee", None, change_kwargs),
        TableItem("Change kwargs to Len Wanger", None, change_kwargs),
        TableItem("Change kwargs to Dick Ellis with lambda", None, lambda tag, ad: ad.update({'first':'Dick', 'last': 'Ellis'})),
        TableItem("call default action (print args and kwargs)", None, TABLE_ITEM_DEFAULT),
        TableItem("call action_1 (print args and kwargs)", None, action_1),
    ]

    my_profile = {'first': 'Len', 'last': 'Wanger'}

    print('\nmenu.run - with sub-menu\n')
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    menu = Table(menu_choices, add_exit=True, style=use_style, default_action=default_action, action_dict=my_profile)
    menu.run()
    print('done')


def change_first_name(row, action_dict):
    result = get_string(prompt='Enter a new first name', default=action_dict['first'])
    action_dict['first'] = result

def change_last_name(row, action_dict):
    result = get_string(prompt='Enter a new last name', default=action_dict['last'])
    action_dict['last'] = result

def test_refresh_table():
    print('test refresh option in a menu:\n')
    my_profile = {'first': 'Len', 'last': 'Wanger'}

    menu_choices = [
        TableItem("Change first name from: {first}", None, change_first_name),
        TableItem("Change last name from: {last}", None, change_last_name),
        TableItem("Change kwargs to Dick Ellis with lambda", None, lambda tag, ad: ad.update({'first':'Dick', 'last': 'Ellis'})),
        TableItem("call default action (print args and kwargs)", None, TABLE_ITEM_DEFAULT),
        TableItem("call action_1 (print args and kwargs)", None, action_1),
    ]

    print('\nmenu.run - dynamic labels - now w/ refresh\n')
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    menu = Table(menu_choices, add_exit=True, style=use_style, default_action=default_action, action_dict=my_profile, refresh=True)
    menu.run()

    print('done')

#
# item_filter example: Filter the menu items by user roles
#
def show_roles(row, action_dict):
    # an action item to print the user's roles
    print('called show_roles: user={} {}, roles={}'.format(action_dict['first'], action_dict['last'], action_dict['roles']))
    return True

def change_roles(row, action_dict):
    # an action item to get a new list of roles for the user
    role_validator = ChoiceValidator(['admin', 'editor', 'user'])
    prompt_str = 'Enter roles for user {} {}'.format(action_dict['first'], action_dict['last'])
    # Fixing: this passed elem_validators, which get_list has never had -- it landed in the
    # **options bag, was forwarded to GetInput and logged as an unknown option, so this demo
    # accepted any role at all while appearing to check them against the list above. Per-element
    # validation goes through elem_get_input, which get_list applies to each value in turn.
    elem_get_input = GetInput(validators=role_validator)
    result = get_list(prompt=prompt_str, default=action_dict['roles'], elem_get_input=elem_get_input)
    action_dict['roles'] = set(result)
    return result

class IntersectionValidator(Validator):
    def __init__(self, choices=None):
        if choices is None:
            self._choices = {}
        else:
            self._choices = set(choices)

    def __call__(self, value, error_callback, validator_fmt_str):
        sv = set(value)
        if len(sv.intersection(self._choices)) != 0:
            return True
        else:
            return False

def role_item_filter(row, action_dict):
    # check if the roles in action_dict for the current user matches any of the required roles for the menu item
    if row.item_data is None or row.action in {TABLE_ITEM_EXIT, TABLE_ITEM_RETURN}:
        return (False, True)

    try:
        role_validator = IntersectionValidator(row.item_data['roles'])
        # error_callback was None, which raises TypeError the moment a validator actually fails --
        # here that is the ordinary case of a user without the role. silent_error is the supported
        # way to ask for no message, and this filter wants none: it hides the row instead.
        if validate(action_dict['roles'], role_validator, error_callback=silent_error):
            return (False, True)

    except (TypeError, KeyError):
        # return (True, False)
        pass

    return (True, False)


def test_item_filter():
    all_roles = {'roles': {'admin', 'user'}}
    admin_only = {'roles': {'admin'}}

    menu_choices = [
        TableItem("Change roles from: {roles}", None, change_roles, item_data=all_roles),
        TableItem("Change roles to: 'admin'", None, lambda tag, ad: ad.update({'roles': {'admin'}}), item_data=all_roles),
        TableItem("call default action (print args and kwargs) - admin only!", None, lambda tag, ad: print('roles={}'.format(ad['roles'])), item_data=admin_only),
        TableItem("call show_roles", None, show_roles),
    ]

    print('\nmenu.run\n')
    my_profile = {'first': 'Len', 'last': 'Wanger', 'roles': ['user'] }
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    menu = Table(menu_choices, add_exit=True, style=use_style, default_action=default_action, action_dict=my_profile, refresh=True, item_filter=role_item_filter)
    menu.run()

    print('done')

#### Dynamic menu from DB stuff ####
def menu_item_factory(row, item_data):
    return TableItem(row['fullname'], None, TABLE_ITEM_DEFAULT, item_data)


def user_filter(table_item, action_dict):
    # Only allow user names starting with W or E
    name = table_item.values[0]
    if name[0] in {'W', 'E'}:
        return (False, True)
    else:
        return (True, False)

CREATE_USERS_SQL = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        fullname TEXT,
        password TEXT
    )
"""

INSERT_USER_SQL = 'INSERT INTO users (name, fullname, password) VALUES (?, ?, ?)'

SEED_USERS = [
    ('ed', 'Ed Jones', 'edspassword'),
    ('wendy', 'Wendy Williams', 'foobar'),
    ('mary', 'Mary Contrary', 'xxg527'),
    ('fred', 'Fred Flinstone', 'blah'),
]


def make_users_db(echo=False):
    """Create an in-memory users table seeded with SEED_USERS and return the open connection.

    Args:
        echo: if True, print each SQL statement as sqlite runs it.

    Returns:
        An open sqlite3.Connection whose rows come back as sqlite3.Row, so the table item
        factories can address columns by name.
    """
    connection = sqlite3.connect(':memory:')
    connection.row_factory = sqlite3.Row

    if echo:
        connection.set_trace_callback(print)

    with connection:  # commits the schema and the seed rows as one transaction
        connection.execute(CREATE_USERS_SQL)
        connection.executemany(INSERT_USER_SQL, SEED_USERS)

    return connection


def load_menu_items(connection):
    """Query the users table and build one TableItem per user, ordered by full name.

    Args:
        connection: an open sqlite3.Connection returned by make_users_db.

    Returns:
        A list of TableItem, one for each row currently in the users table.
    """
    cursor = connection.execute('SELECT name, fullname FROM users ORDER BY fullname')
    return [menu_item_factory(row, item_data={'min_len': 3}) for row in cursor]


def show_menu_items(label, items):
    print(label)
    for item in items:
        print(item)


def test_dynamic_menu_from_db(filter_items=False):
    with closing(make_users_db(echo=True)) as connection:
        tis = load_menu_items(connection)
        show_menu_items('users before the insert:', tis)

        # Winnie's full name starts with W, so she survives user_filter too and the refresh
        # is visible whether or not the menu is filtered.
        print('adding winnie')
        with connection:
            connection.execute(INSERT_USER_SQL, ('winnie', 'Winnie Winn', 'winniespassword'))

        # Rebuilding tis from a second query is what picks up the new user: the first query's
        # rows were read out of the cursor and turned into TableItems, so that list is a
        # snapshot and cannot see later inserts. The menu below is built from the fresh list.
        tis = load_menu_items(connection)
        show_menu_items('users after the insert (refreshed from the db):', tis)

        use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)

        if filter_items:
            menu = Table(rows=tis, add_exit=True, style=use_style, item_filter=user_filter)
        else:
            menu = Table(rows=tis, add_exit=True, style=use_style)

        menu()
#### End of Dynamic menu from DB stuff ####


def menu_item_factory2(row, min_len):
    # test item factory that sets the item to hidden if it's shorter than the minimum length set in the item_data dict
    if len(row['name']) > min_len-1:
        return TableItem(row['fullname'], None, TABLE_ITEM_DEFAULT)
    else:  # hide short names!
        return TableItem(row['fullname'], None, TABLE_ITEM_DEFAULT, hidden=True, enabled=True)

def set_filter_len_action(row, action_dict):
    result = get_int(prompt='Enter the minimum user name length to show', minimum=0)
    action_dict['min_len'] = result

def user_filter2(table_item, action_dict):
    # Only allow user names whose length is >= the min length
    if table_item.item_data and 'no_filter' in table_item.item_data:
        return (False, True)

    first_name = table_item.values[0].split()[0]
    if len(first_name) >= action_dict['min_len']:
        return (False, True)
    else:
        return (True, False)


def test_dynamic_menu_from_list(filter_items=False):
    users = [
        { 'name':'ed', 'fullname': 'Ed Jones', 'password': 'edspassword' },
        { 'name':'wendy', 'fullname': 'Wendy Williams', 'password': 'foobar' },
        { 'name':'mary', 'fullname': 'Mary Contrary', 'password': 'xxg527' },
        { 'name':'leonard', 'fullname': 'Leonard Nemoy', 'password': 'spock' },
        { 'name':'fred', 'fullname': 'Fred Flintstone', 'password': 'blah'  } ]

    action_dict = {'min_len': 4}
    tis = [menu_item_factory2(user, 4) for user in users]
    tis.append(TableItem('Set minimum length ({min_len})', 'filter', set_filter_len_action, hidden=True,
                         item_data={'no_filter': True}))   # no_filter tells item_filter not to filter the item

    header = 'Showing users with user length > {min_len}\n'
    footer = 'type "filter" to change minimum length'
    use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    menu = Table(rows=tis, add_exit=True, style=use_style, action_dict=action_dict, header=header, footer=footer, item_filter=user_filter2)
    menu()


if __name__ == '__main__':
    if False:
        pass

    test_get_menu_1()
    test_get_menu_2()
    test_action_table()
    test_sub_table()
    test_args_table()
    test_refresh_table()
    test_item_filter()
    test_dynamic_menu_from_db(filter_items=False)
    test_dynamic_menu_from_db(filter_items=True)
    test_dynamic_menu_from_list()



