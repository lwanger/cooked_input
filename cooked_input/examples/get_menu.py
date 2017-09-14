"""
cooked input example of using table input to pick from a menu.

Len Wanger, 2017
"""

from collections import namedtuple
# from cooked_input import get_int
from cooked_input import get_menu

"""
# old way:
# Define actions for menu items
def do_action_1():
    print('\nCalled do_action 1')

def do_action_2():
    print('\nCalled do_action 2')

def do_action_3():
    print('\nCalled do_action 3')


def show_menu(menu_table):
    print('\nMenu:')
    for i,item in enumerate(menu_table):
        print('\t{}.\t{}'.format(i+1, item[1]))


if __name__ == '__main__':
    MenuItem = namedtuple('MenuItem', 'tag desc action')
    menu_items = [
        MenuItem('ACTION_1', 'Do action number 1', do_action_1),
        MenuItem('ACTION_2', 'Do action number 2', do_action_2),
        MenuItem('ACTION_3', 'Do action number 3', do_action_3),
        MenuItem('QUIT', 'Quit', None)
    ]

    menu_table = [(i + 1, menu_item.desc) for i, menu_item in enumerate(menu_items)]
    prompt_str = 'What would you like to do?'
    error_fmt = 'Not a valid menu choice'

    while True:
        show_menu(menu_table)
        menu_choice = get_int(minimum=1, maximum=len(menu_table), prompt=prompt_str, validator_error_fmt=error_fmt)
        item = menu_items[menu_choice - 1]

        if item.tag == 'QUIT':
            break
        else:
            item.action()
"""

if __name__ == '__main__':
    # new way
    choices = ['red', 'blue', 'green']

    print('test_get_menu:\n')
    print('simplest case:\n')
    result = get_menu(choices)
    print('result={}'.format(result))

    print('\nwith options...\n')
    result = get_menu(choices, title='My Menu', prompt="Choose m'lady", default_choice='red', add_exit=True,
                      case_sensitive=True)
    print('result={}'.format(result))