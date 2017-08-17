
from io_get_input import get_table_input
from io_get_input.convertors import IntConvertor
from io_get_input.validators import InRangeValidator
from collections import namedtuple

if __name__ == '__main__':
    # changing the user roles changes the menu choices available.
    user_roles = {'editor', 'user'}
    # user_roles = {'admin'}

    MenuItem = namedtuple('MenuItem', 'item_id item_str roles')
    menu_items = [
        MenuItem('DO_ACTION_1', 'Do action number 1', {'all'}),
        MenuItem('DO_ACTION_2', 'Do action number 2', {'all'}),
        MenuItem('DO_ACTION_3', 'Do action number 3', {'admin'}),
        MenuItem('DO_ACTION_4', 'Do action number 4', {'user'}),
        MenuItem('DO_ACTION_5', 'Do action number 5', {'editor'}),
        MenuItem('QUIT', 'Quit', {'all'})
    ]

    menu_choices = [item for item in menu_items if
                    ('admin' in user_roles) or ('all' in item.roles) or (item.roles.intersection(user_roles))]
    menu_table = [(i + 1, menu_item.item_str) for i, menu_item in enumerate(menu_choices)]
    menu_validator = InRangeValidator(min_val=1, max_val=len(menu_table))

    while True:
        print('\n')
        print('Menu:')

        try:
            print('')
            num = get_table_input(menu_table, cleaners=None, convertor=IntConvertor(),
                                   validators=menu_validator, prompt='What would you like to do?',
                                   input_value=False, return_value=False, show_table=True)
            item_id = menu_choices[num-1].item_id

            if item_id == 'DO_ACTION_1':
                print('Doing action 1...')
            elif item_id == 'DO_ACTION_2':
                print('Doing action 2...')
            elif item_id == 'DO_ACTION_3':
                print('Doing action 3...')
            elif item_id == 'DO_ACTION_4':
                print('Doing action 4...')
            elif item_id == 'DO_ACTION_5':
                print('Doing action 5...')
            elif item_id == 'QUIT':
                break
            else:
                print('Error: Not a valid menu choice. Please retry.')
        except ValueError:
            print('Error: please type in a number for the menu choice.')

