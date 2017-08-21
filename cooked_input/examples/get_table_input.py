"""
cooked input examples of getting inputs from tables

Len Wanger, 2017
"""

import cooked_input
from cooked_input import get_table_input


if __name__ == '__main__':
    table = [(1, 'red'), (2, 'blue'), (4, 'green'), (6, 'yellow')]
    cur_val = 'red'

    color = get_table_input(table=table, cleaners=None, convertor=None, validators=None, input_value=cooked_input.TABLE_ID, return_value=cooked_input.TABLE_ID, show_table=True,
                             prompt='Enter the id of the color you want', value_error='a valid color id')
    print('color id=%d' % (color))

    color = get_table_input(table=table, cleaners=None, convertor=None, validators=None, input_value=cooked_input.TABLE_ID, return_value=cooked_input.TABLE_VALUE, show_table=True,
                                 default=cur_val, prompt='Enter the id of the color you want', value_error='a valid color id')
    print('color=%s' % (color))

    color = get_table_input(table=table, cleaners=None, convertor=None, validators=None, input_value=cooked_input.TABLE_VALUE, return_value=cooked_input.TABLE_VALUE, show_table=True,
                                 default=cur_val, prompt='Enter the name of color you want', value_error='a valid color name')
    print('color=%s' % (color))

    color = get_table_input(table=table, cleaners=None, convertor=None, validators=None, input_value=cooked_input.TABLE_ID_OR_VALUE, return_value=cooked_input.TABLE_VALUE, show_table=True,
                                 prompt='Enter the name or id of the color you want', value_error='a valid color name or id')
    print('color=%s' % (color))
