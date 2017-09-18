"""
cooked input example of using table input to pick from a menu.

Len Wanger, 2017
"""

from cooked_input import get_menu, get_string
from cooked_input import Menu, MenuItem, MENU_DEFAULT_ACTION, MENU_ACTION_EXIT, MENU_ADD_RETURN, MENU_ADD_EXIT


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
    result = get_menu(choices, title='My Menu', prompt=prompt_str, default_choice='red', add_exit=MENU_ADD_EXIT,
                      case_sensitive=True)
    print('result={}'.format(result))


def default_action(tag, kwargs):
    print('called default_action, tag={}, kwargs={}'.format(tag, kwargs))
    return True


def action_1(text, kwargs):
    print('called action_1, text={}, kwargs={}'.format(text, kwargs))
    return True


def show_choice(menu, choice):
    action = menu.get_action(choice)
    print('choice={}, action={}'.format(choice, action))
    menu.do_action(choice)


def test_action_menu():
    menu_choices = [
        MenuItem("Choice 1 - no specified tag, no specified action", None, None),
        MenuItem("Choice 2 - default action", 2, MENU_DEFAULT_ACTION),
        MenuItem("Choice 3 - text tag, lambda action", 'foo', lambda tag,kwargs: print('lambda action: tag={}, kwargs={}'.format(tag,kwargs))),
        MenuItem("Choice 4 - text tag, action handler function specified", 'bar', action_1),
        MenuItem("STOP the menu!", 'stop', MENU_ACTION_EXIT),
    ]

    print('\nget_menu_choice - add_exit=True\n')
    menu = Menu(menu_choices[:-1])
    choice = menu.get_menu_choice()
    show_choice(menu, choice)

    print('\nget_menu_choice - add_exit=False (no exit!), case_sensitive=True, with title\n')
    menu = Menu(menu_choices[:-1], title='My Menu:', add_exit=False, case_sensitive=True)
    choice = menu.get_menu_choice()
    show_choice(menu, choice)

    print('\nget_menu_choice - add_exit=False, w/ prompt, default="stop"\n')
    menu = Menu(menu_choices, prompt='Choose or die!', default_choice='stop', default_action=default_action, add_exit=False)
    choice = menu.get_menu_choice()
    show_choice(menu, choice)

    print('\nmenu.run - add_exit=True\n')
    menu.run()
    print('done')


def sub_menu_action(tag, kwargs):
    print('sub_menu2: tag={}, kwargs={}'.format(tag, kwargs))

    sub_menu_choices = [
        MenuItem("sub menu 2: Choice 1", 1, MENU_DEFAULT_ACTION),
        MenuItem("sub menu 2: Choice 2", 2, MENU_DEFAULT_ACTION),
    ]
    sub_menu = Menu(sub_menu_choices, title="Sub-Menu 2", add_exit=MENU_ADD_RETURN)
    sub_menu.run()


def test_sub_menu():
    sub_menu_1_items = [
        MenuItem("sub menu 1: Choice 1", 1, MENU_DEFAULT_ACTION),
        MenuItem("sub menu 1: Choice 2", 2, MENU_DEFAULT_ACTION),
    ]
    sub_menu_1 = Menu(sub_menu_1_items, title="Sub-Menu 2", add_exit=MENU_ADD_RETURN)

    # call submenus two different ways. First by using it as a callable, which calls run on the sub_menu, and second
    # with an explicit action handler
    menu_choices = [
        MenuItem("Choice 1", None, MENU_DEFAULT_ACTION),
        MenuItem("sub_menu 1", None, sub_menu_1),
        MenuItem("sub_menu 2", None, sub_menu_action),
    ]

    print('\nmenu.run - with sub-menu\n')
    menu = Menu(menu_choices, )
    menu.run()
    print('done')


def change_kwargs(tag, action_dict):
    # Change the action_dict values...
    if tag == 1:
        action_dict['first'] = 'Ron'
        action_dict['last'] = 'McGee'
    elif tag == 2:
        action_dict['first'] = 'Len'
        action_dict['last'] = 'Wanger'

    print(f'kwargs={action_dict}')
    return action_dict

def test_args_menu():
    print('test sending args and kwargs to menus:\n')

    menu_choices = [
        MenuItem("Change kwargs to Ron McGee", None, change_kwargs),
        MenuItem("Change kwargs to Len Wanger", None, change_kwargs),
        MenuItem("Change kwargs to Dick Ellis with lambda", None, lambda tag, ad: ad.update({'first':'Dick', 'last': 'Ellis'})),
        MenuItem("call default action (print args and kwargs)", None, MENU_DEFAULT_ACTION),
        MenuItem("call action_1 (print args and kwargs)", None, action_1),
    ]

    my_profile = {'first': 'Len', 'last': 'Wanger'}

    print('\nmenu.run - with sub-menu\n')
    menu = Menu(menu_choices, default_action=default_action, action_dict=my_profile)
    menu.run()
    print('done')


def change_first_name(tag, action_dict):
    result = get_string(prompt='Enter a new first name', default=action_dict['first'])
    action_dict['first'] = result

def change_last_name(tag, action_dict):
    result = get_string(prompt='Enter a new last name', default=action_dict['last'])
    action_dict['last'] = result

def test_refresh_menu():
    print('test refresh option in a menu:\n')
    my_profile = {'first': 'Len', 'last': 'Wanger'}

    menu_choices = [
        MenuItem("Change first name from: {first}", None, change_first_name),
        MenuItem("Change last name from: {last}", None, change_last_name),
        MenuItem("Change kwargs to Dick Ellis with lambda", None, lambda tag, ad: ad.update({'first':'Dick', 'last': 'Ellis'})),
        MenuItem("call default action (print args and kwargs)", None, MENU_DEFAULT_ACTION),
        MenuItem("call action_1 (print args and kwargs)", None, action_1),
    ]

    print('\nmenu.run - dynamic labels - now w/ refresh\n')
    menu = Menu(menu_choices, default_action=default_action, action_dict=my_profile, refresh=True)
    menu.run()

    print('done')


if __name__ == '__main__':
    test_get_menu_1()
    test_get_menu_2()
    # test_action_menu()
    # test_sub_menu()
    # test_args_menu()
    test_refresh_menu()




