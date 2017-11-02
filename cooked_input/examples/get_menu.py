"""
cooked input example of using table input to pick from a menu.

Len Wanger, 2017
"""

# from collections import namedtuple

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker

from cooked_input import get_menu, get_string, get_int, get_list, validate, Validator, ChoiceValidator
# from cooked_input import Table, TableItem, DynamicTableItem, TABLE_DEFAULT_ACTION, TABLE_ACTION_EXIT, TABLE_ACTION_RETURN, TABLE_ADD_RETURN, TABLE_ADD_EXIT
from cooked_input import Table
from cooked_input import TableItem, DynamicTableItem, TABLE_DEFAULT_ACTION, TABLE_ACTION_EXIT, TABLE_ACTION_RETURN, TABLE_ADD_RETURN, TABLE_ADD_EXIT


def test_get_menu_1():
    choices = ['red', 'blue', 'green']
    print('test_get_menu:\n')
    print('simplest case:\n')
    result = get_menu(choices)
    print('result={}'.format(result))


def test_get_menu_2():
    choices = ['red', 'blue', 'green']
    print('\nwith options...\n')
    # error_fmt = 'Not a valid menu choice'
    prompt_str = 'Enter a menu choice'
    result = get_menu(choices, title='My Menu', prompt=prompt_str, default_choice='red', add_exit=TABLE_ADD_EXIT,
                      case_sensitive=True)
    print('result={}'.format(result))


def default_action(row, kwargs):
    print('called default_action, tag={}, row={}, kwargs={}'.format(row.tag, row, kwargs))
    return True


def action_1(row, action_dict):
    print('called action_1, tag={}, row={}, action_dict={}'.format(row.tag, row, action_dict))
    return True


def show_choice(menu, choice):
    action = menu.get_action(choice.tag)
    print('choice={}, action={}'.format(choice, action))
    # menu.do_action(choice.tag)
    menu.do_action(choice)


def test_action_Table():
    menu_choices = [
        TableItem("Choice 1 - no specified tag, no specified action", None, None),
        TableItem("Choice 2 - default action", 2, TABLE_DEFAULT_ACTION),
        TableItem("Choice 3 - text tag, lambda action", 'foo', lambda row,kwargs: print('lambda action: row={}, kwargs={}'.format(row,kwargs))),
        TableItem("Choice 4 - text tag, action handler function specified", 'bar', action_1),
        TableItem("STOP the menu!", 'stop', TABLE_ACTION_EXIT),
    ]

    print('\nget_table_choice - add_exit=True\n')
    menu = Table(menu_choices[:-1])
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nget_table_choice - add_exit=False (no exit!), case_sensitive=True, with title\n')
    menu = Table(menu_choices[:-1], title='My Menu:', add_exit=False, case_sensitive=True)
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nget_table_choice - add_exit=False, w/ prompt, default="stop"\n')
    menu = Table(menu_choices, prompt='Choose or die!', default_choice='stop', default_action=default_action, add_exit=False)
    choice = menu.get_table_choice()
    show_choice(menu, choice)

    print('\nmenu.run - add_exit=True\n')
    menu.run()
    print('done')


def sub_menu_action(row, action_dict):
    print('sub_menu2: row={}, action_dict={}'.format(row, action_dict))

    sub_menu_choices = [
        TableItem("sub menu 2: Choice 1", 1, TABLE_DEFAULT_ACTION),
        TableItem("sub menu 2: Choice 2", 2, TABLE_DEFAULT_ACTION),
    ]
    sub_menu = Table(sub_menu_choices, title="Sub-Menu 2", add_exit=TABLE_ADD_RETURN)
    sub_menu.run()


def test_sub_Table():
    sub_menu_1_items = [
        TableItem("sub menu 1: Choice 1", 1, TABLE_DEFAULT_ACTION),
        TableItem("sub menu 1: Choice 2", 2, TABLE_DEFAULT_ACTION),
    ]
    sub_menu_1 = Table(sub_menu_1_items, title="Sub-Menu 2", add_exit=TABLE_ADD_RETURN)

    # call submenus two different ways. First by using it as a callable, which calls run on the sub_menu, and second
    # with an explicit action handler
    menu_choices = [
        TableItem("Choice 1", None, TABLE_DEFAULT_ACTION),
        TableItem("sub_menu 1", None, sub_menu_1),
        TableItem("sub_menu 2", None, sub_menu_action),
    ]

    print('\nmenu.run - with sub-menu\n')
    menu = Table(menu_choices, )
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

def test_args_Table():
    print('test sending args and kwargs to menus:\n')

    menu_choices = [
        TableItem("Change kwargs to Ron McGee", None, change_kwargs),
        TableItem("Change kwargs to Len Wanger", None, change_kwargs),
        TableItem("Change kwargs to Dick Ellis with lambda", None, lambda tag, ad: ad.update({'first':'Dick', 'last': 'Ellis'})),
        TableItem("call default action (print args and kwargs)", None, TABLE_DEFAULT_ACTION),
        TableItem("call action_1 (print args and kwargs)", None, action_1),
    ]

    my_profile = {'first': 'Len', 'last': 'Wanger'}

    print('\nmenu.run - with sub-menu\n')
    menu = Table(menu_choices, default_action=default_action, action_dict=my_profile)
    menu.run()
    print('done')


def change_first_name(row, action_dict):
    result = get_string(prompt='Enter a new first name', default=action_dict['first'])
    action_dict['first'] = result

def change_last_name(row, action_dict):
    result = get_string(prompt='Enter a new last name', default=action_dict['last'])
    action_dict['last'] = result

def test_refresh_Table():
    print('test refresh option in a menu:\n')
    my_profile = {'first': 'Len', 'last': 'Wanger'}

    menu_choices = [
        TableItem("Change first name from: {first}", None, change_first_name),
        TableItem("Change last name from: {last}", None, change_last_name),
        TableItem("Change kwargs to Dick Ellis with lambda", None, lambda tag, ad: ad.update({'first':'Dick', 'last': 'Ellis'})),
        TableItem("call default action (print args and kwargs)", None, TABLE_DEFAULT_ACTION),
        TableItem("call action_1 (print args and kwargs)", None, action_1),
    ]

    print('\nmenu.run - dynamic labels - now w/ refresh\n')
    menu = Table(menu_choices, default_action=default_action, action_dict=my_profile, refresh=True)
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
    result = get_list(prompt=prompt_str, default=action_dict['roles'], elem_validators=role_validator)
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
    if row.item_data == None or row.action in {TABLE_ACTION_EXIT, TABLE_ACTION_RETURN}:
        return True

    try:
        role_validator = IntersectionValidator(row.item_data['roles'])
        return validate(action_dict['roles'], role_validator, error_callback=None)
    except (TypeError, KeyError):
        return False

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
    menu = Table(menu_choices, default_action=default_action, action_dict=my_profile, refresh=True, item_filter=role_item_filter)
    menu.run()

    print('done')

#### Dynamic menu from DB stuff ####
def menu_item_factory(i, row, item_data):
    return TableItem(row.fullname, None, TABLE_DEFAULT_ACTION, item_data)


def user_filter(row, action_dict):
    # Only allow user names starting with W or E
    # if row.text[0] in {'W', 'E'}:
    name = row.values[0]
    if name[0] in {'W', 'E'}:
        return True
    else:
        return False

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)

def test_dynamic_menu_from_db(filter_items=False):
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    session.add_all([
        User(name='ed', fullname='Ed Jones', password='edspassword'),
        User(name='wendy', fullname='Wendy Williams', password='foobar'),
        User(name='mary', fullname='Mary Contrary', password='xxg527'),
        User(name='fred', fullname='Fred Flinstone', password='blah')])

    session.commit()

    # qry = session.query(User.name, User.fullname)
    qry = session.query(User.name, User.fullname).order_by(User.fullname)
    # qry = session.query(User.name, User.fullname).filter(User.name=='ed')
    # dmi = DynamicTableItem(qry, menu_item_factory, item_data=None)
    dmi = DynamicTableItem(qry, menu_item_factory, item_data={'min_len':3})
    for row in dmi():
        print(row)

    print('adding foo')  # show that the stored query will update with data changes
    session.add(User(name='foo', fullname='Foo Winn', password='foospassword'))
    session.commit()

    if filter_items:
        menu = Table(rows=dmi, item_filter=user_filter)
    else:
        menu = Table(rows=dmi)

    # Table()
    menu()
#### End of Dynamic menu from DB stuff ####

def menu_item_factory(i, row, item_data):
    # test item factory that sets the item to hidden if it's shorter than the minimum length set in the item_data dict
    if len(row.name)> item_data['min_len']-1:
        return TableItem(row.fullname, None, TABLE_DEFAULT_ACTION)
    else:  # hide short names!
        return TableItem(row.fullname, None, TABLE_DEFAULT_ACTION, hidden=True, enabled=False)

def menu_item_factory2(i, row, item_data):
    # test item factory that sets the item to hidden if it's shorter than the minimum length set in the item_data dict
    if len(row['name'])> item_data['min_len']-1:
        return TableItem(row['fullname'], None, TABLE_DEFAULT_ACTION)
    else:  # hide short names!
        return TableItem(row['fullname'], None, TABLE_DEFAULT_ACTION, hidden=True, enabled=False)

def set_filter_len_action(row, action_dict):
    result = get_int(prompt='Enter the minimum user name length to show', minimum=0)
    action_dict['min_len'] = result


def test_dynamic_menu_from_list(filter_items=False):
    users = [
        { 'name':'ed', 'fullname': 'Ed Jones', 'password': 'edspassword' },
        { 'name':'wendy', 'fullname': 'Wendy Williams', 'password': 'foobar' },
        { 'name':'mary', 'fullname': 'Mary Contrary', 'password': 'xxg527' },
        { 'name':'leonard', 'fullname': 'Leonard Nemoy', 'password': 'spock' },
        { 'name':'fred', 'fullname': 'Fred Flinstone', 'password': 'blah'  } ]
        # ['ed', 'Ed Jones', 'edspassword'],
        # ['wendy', 'Wendy Williams', 'foobar'],
        # ['mary', 'Mary Contrary', 'xxg527'],
        # ['leonard', 'Leonard Nemoy', 'spock'],
        # ['fred', 'Fred Flinstone', 'blah']]

    action_dict = {'min_len': 4}
    dmi = [ DynamicTableItem(users, menu_item_factory2, action_dict),
            TableItem('Set minimum length ({min_len})', 'filter', set_filter_len_action, hidden=True)
          ]

    header = 'Showing users with user length > {min_len}\n'
    footer = 'type "filter" to change minimum length'
    menu = Table(rows=dmi, action_dict=action_dict, header=header, footer=footer)
    # Table()
    menu()


#####
if __name__ == '__main__':
    if False:
        pass
    test_get_menu_1()
    test_get_menu_2()
    test_action_Table()
    test_sub_Table()
    test_args_Table()
    test_refresh_Table()
    test_item_filter()
    test_dynamic_menu_from_db(filter_items=False)
    test_dynamic_menu_from_db(filter_items=True)
    test_dynamic_menu_from_list()



