"""
cooked input example of using table input to pick from a menu.

Len Wanger, 2017
"""

from cooked_input import get_menu
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
    result = get_menu(choices, title='My Menu', prompt=prompt_str, default_choice='red', add_exit=True,
                      case_sensitive=True)
    # case_sensitive=True, validator_error_fmt=error_fmt)
    print('result={}'.format(result))

def default_action(tag, *args, **kwargs):
    print('called default_action, tag={}, args={} kwargs={}'.format(tag, args, kwargs))
    return True

def action_1(text, *args, **kwargs):
    print('called action_1, text={}, args={}, kwargs={}'.format(text, args, kwargs))
    return True

def show_choice(menu, choice):
    action = menu.get_action(choice)
    print('choice={}, action={}'.format(choice, action))
    menu.do_action(choice)


def test_action_menu():
    menu_choices = [
        MenuItem("Choice 1", None, None),
        MenuItem("Choice 2", 2, MENU_DEFAULT_ACTION),
        MenuItem("Do Foo", 'foo', MENU_DEFAULT_ACTION),
        MenuItem("Do Bar (action_1)", 'bar', action_1),
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

def sub_menu1(tag, *args, **kwargs):
    print('sub_menu1: tag={}, args={}, kwargs={}'.format(tag, args, kwargs))

    sub_menu_choices = [
        MenuItem("sm1: Choice 1", 1, MENU_DEFAULT_ACTION),
        MenuItem("sm1: Choice 2", 2, MENU_DEFAULT_ACTION),
        MenuItem("Return to parent menu", 3, MENU_ADD_RETURN),
    ]
    sub_menu = Menu(sub_menu_choices, title="Sub-Menu 1", add_exit=False)
    sub_menu.run()


def sub_menu2(tag, *args, **kwargs):
    print('sub_menu1: tag={}, args={}, kwargs={}'.format(tag, args, kwargs))

    sub_menu_choices = [
        MenuItem("sm2: Choice 1", 1, MENU_DEFAULT_ACTION),
        MenuItem("sm2: Choice 2", 2, MENU_DEFAULT_ACTION),
    ]
    sub_menu = Menu(sub_menu_choices, title="Sub-Menu 2", add_exit=MENU_ADD_RETURN)
    sub_menu.run()


def test_sub_menu():
    menu_choices = [
        MenuItem("Choice 1", None, MENU_DEFAULT_ACTION),
        MenuItem("sub_menu 1", None, sub_menu1),
        MenuItem("sub_menu 2", None, sub_menu2),
    ]

    print('\nmenu.run - with sub-menu\n')
    menu = Menu(menu_choices, )
    menu.run()
    print('done')


if __name__ == '__main__':
    # test_get_menu_1()
    # test_get_menu_2()
    # test_action_menu()
    test_sub_menu()



