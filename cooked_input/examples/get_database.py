"""
cooked input example showing how to use with entries from database tables.

Len Wanger, 2017
"""

import sqlite3
from collections import Counter
import cooked_input
from cooked_input import get_table_input

def create_db():
    # Create an in memory sqlite database of hamburger options
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE buns (id INTEGER PRIMARY_KEY, type text, price real)''')
    c.execute("INSERT INTO buns VALUES (1, 'plain',1.00)")
    c.execute("INSERT INTO buns VALUES (2, 'sesame seed',1.25)")
    c.execute("INSERT INTO buns VALUES (3, 'pretzel',1.50)")

    c.execute('''CREATE TABLE patties (id INTEGER PRIMARY_KEY, type text, price real)''')
    c.execute("INSERT INTO patties VALUES (1, 'hamburger',1.00)")
    c.execute("INSERT INTO patties VALUES (2, 'sirloin',2.00)")
    c.execute("INSERT INTO patties VALUES (3, 'chicken',1.50)")
    c.execute("INSERT INTO patties VALUES (4, 'veggie',1.50)")

    c.execute('''CREATE TABLE extras (id INTEGER PRIMARY_KEY, type text, price real)''')
    c.execute("INSERT INTO extras VALUES (1, 'bacon',1.00)")
    c.execute("INSERT INTO extras VALUES (2, 'cheese',1.00)")
    c.execute("INSERT INTO extras VALUES (3, 'special sauce',0.0)")
    c.execute("INSERT INTO extras VALUES (4, 'tomatoes',0.0)")
    c.execute("INSERT INTO extras VALUES (5, 'grilled onions',0.50)")
    c.execute("INSERT INTO extras VALUES (6, 'lettuce',0.0)")
    c.execute("INSERT INTO extras VALUES (7, 'pickles',0.0)")

    conn.commit()
    return conn, c


if __name__ == '__main__':
    print('\nBuild your burger!')
    print('==================\n')
    price = 0.0
    conn, cursor = create_db()

    # Get the bun type
    cursor.execute('SELECT * FROM buns ORDER BY price')
    buns = { bun[0]: (bun[1], bun[2]) for bun in cursor.fetchall() }
    table = [ (k, '{}'.format(v[0], v[1])) for k,v in buns.items() ]
    default_val = 'plain'
    bun = get_table_input(table=table, input_value=cooked_input.TABLE_ID_OR_VALUE, return_value=cooked_input.TABLE_ID,
                            show_table=True, default=default_val, prompt='Which kind of bun do you want', value_error='a valid bun id or type')
    price += buns[bun][1]

    # Get the patty type
    cursor.execute('SELECT * FROM patties ORDER BY price')
    patties = {patty[0]: (patty[1], patty[2]) for patty in cursor.fetchall()}
    table = [(k, '{}'.format(v[0], v[1])) for k, v in patties.items()]
    default_val = 'hamburger'
    patty = get_table_input(table=table, input_value=cooked_input.TABLE_ID_OR_VALUE, return_value=cooked_input.TABLE_ID,
                                default=default_val, prompt='Which kind of patty do you want', value_error='a valid patty id or type')
    price += patties[patty][1]

    # Get the options - note: allow an arbitrary of options, and keep track of how many of each
    options = []
    cursor.execute('SELECT * FROM extras')
    extras = {extra[0]: (extra[1], extra[2]) for extra in cursor.fetchall()}
    table = [(k, '{}'.format(v[0], v[1])) for k, v in extras.items()]

    while True:
        extra = get_table_input(table=table, cleaners=None, convertor=None, validators=None,
                                input_value=cooked_input.TABLE_ID_OR_VALUE, return_value=cooked_input.TABLE_ID,
                                prompt='Which kind of extra do you want (hit return when done choosing extras)',
                                value_error='a valid extra id or type', required=True)
        if extra is None:
            break
        else:
            options.append(extra)
            price += extras[extra][1]

    option_counter = Counter(options)

    print('\nSummary of your burger:')
    print('=======================\n')
    print('{} bun: ${:.2f}'.format(buns[bun][0], buns[bun][1]))
    print('{} patty: ${:.2f}'.format(patties[patty][0], patties[patty][1]))

    if len(options) > 0:
        print('Extras:')
        for option, count in option_counter.items():
            if count == 1:
                print('\t{}: ${:.2f}'.format(extras[option][0], extras[option][1]))
            else:
                print('\t{}x {}: ${:.2f}'.format(count, extras[option][0], extras[option][1]))

    print('\ntotal price: \t${:.2f}'.format(price))
    conn.close()
