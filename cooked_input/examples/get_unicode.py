#!/usr/local/bin/python
# coding: latin-1

"""
Test cooked_input table to create a Unicode character picker

Len Wanger, 2017

unicode data information:
    https://docs.python.org/3.1/library/unicodedata.html

    methods:

        unicodedata.lookup(name)
        unicodedata.name(chr[, default])
        unicodedata.decimal(chr[, default])
        unicodedata.digit(chr[, default])
        unicodedata.numeric(chr[, default])
        unicodedata.category(chr)
        unicodedata.bidirectional(chr)
        unicodedata.combining(chr)
        unicodedata.east_asian_width(chr)
        unicodedata.mirrored(chr)
        unicodedata.decomposition(chr)
        unicodedata.normalize(form, unistr) - Valid values for form are ‘NFC’, ‘NFKC’, ‘NFD’, and ‘NFKD’
        ...

unicode information:
    http://www.unicode.org/Public/5.1.0/ucd/UCD.html
    emoji's: https://www.unicode.org/emoji/charts/full-emoji-list.html

    code charts: https://www.unicode.org/Public/UCD/latest/charts/CodeCharts.pdf
        basic latin: 0000-00FF
        latin extended: 0100-024F
        spacing and modifiers: 02B0-02FF
        greek: 0370-03FF
        hebrew: 0590-05FF
        superscripts and subscripts: 2070-209F
        currency: 20A0-20CF
        math operators: 2200-22FF
        technical: 2300-23FF
        box drawing: 2500-257F
        block elements: 2580-259F
        misc symbols: 2600-26FF
        dingbats: 2700-27BF
        muscial symbols: 1D100-1D1FF
        emoticons: 1F600-1F64F

    utf-8 is: https://en.wikipedia.org/wiki/UTF-8, single octet - 0000-007F



    modifiers:
        Lu - letter, u - uppercase, l - lowercase, t - titlecase, m - modifier, 0 - other
        Mn - mark, n - non-spacing, c - spacing combining, e - enclosing
        Nd - number, d - decimal digit, l - letter, o - other
        Pc - punctuation, c - connector, d - dash, s - open, e - close, i - initial quote, f- final quote, 0 - other
        Sm - symbol, m - math, c - currency, k - modifier, o - other
        Zd - separator, s - space, l - line, p - paragraph
        Cc - other, c - control, f - format, s- surrogate, o - private use, n - not assinged


    In windows console type: chcp 65001 to display unicode

TODO:
    - display and pick from table
    - do paged table and navigation cmds/keys
    - do filtering by name, cleass, bidirectional, combining, text search...
        - util to create a set of all of the categories and properties?
    - do it as emoji picker vs others... (range of code points for table?)

show table with - character, digit, u\ form, category, name/description?
"""

import unicodedata
import win_unicode_console

from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding.manager import Registry
from prompt_toolkit.key_binding.manager import KeyBindingManager
from cooked_input import default_key_registry


import cooked_input as ci


def print_chars(start=32, end=0x007F):
    for i in range(start,end):
        ch = chr(i)
        try:
            name = unicodedata.name(ch)
            s = '{}\t{}\t{}\t{}'.format(i, ch, unicodedata.category(ch), name)
            print(s)
        except (ValueError) as err:
            # value errors on 0..31, 127..159, ...
            # print('ValueError (i={})'.format(i))
            name = 'n/a'
        except (UnicodeEncodeError) as err:
            print('UnicodeEncodeError: couldn\'t encode char {}'.format(i))


def unicode_item_filter(item, action_dict):
    # filter values in action_dict:
    #   cat_filter - filter for the category. if None ignore filter. 'L*' filters any Letter category
    #   name_filter is a keyword to find the the char name, None for no filter
    #   item_data ['filter_proof'] True then passes filter automatically

    try:
        if item.item_data and item.item_data['filter_proof'] is True:
            return True
    except KeyError:
        pass

    try:
        cat_filter = action_dict['cat_filter']
        in_name = action_dict['name_filter']
    except (KeyError):
        return True

    cat1 = cat2 = None

    if cat_filter is not None and len(cat_filter) == 2:
        cat1 = cat_filter[0] if cat_filter[0] != '*' else None
        cat2 = cat_filter[1] if cat_filter[1] != '*' else None

    # ch = item.values[0]
    ch_name = item.values[1]
    ch_cat = item.values[2]

    try:
        if (cat1 is None or ch_cat[0]==cat1) and (cat2 is None or ch_cat[1]==cat2) and (in_name is None or in_name in ch_name):
            return True
    except (IndexError, TypeError):
        pass

    return False

def next_page_action(row, action_dict):
    table = action_dict['table']
    table.page_down()

def make_table(start=32, end=0x007F, cat_filter='**', name_filter=''):
    """
    Creates and returns a cooked_input table containing Unicode characters (with ordinal values from start to end). The
    cat_filter and name_filter are added to the action_dict and used as an item filter for the table. For instance to look
    for letters use cat_filter 'L*', for upper case letters 'Lu', and for currency symbols '*c'. name_filter looks for a
    substring in the unicode character name. For example to fine a latin character use 'LATIN'.

     Navigation keys...
    """
    tis = []
    col_names = "Character Category Name".split()
    for i in range(start,end):
        try:
            ch = chr(i)
            name = unicodedata.name(ch)
            cat = unicodedata.category(ch)
            ti = ci.TableItem(col_values=[ch, name, cat], tag=i)
            tis.append(ti)
        except (ValueError) as err:
            # print('ValueError (i={})'.format(i))
            name = 'n/a'
        except (UnicodeEncodeError) as err:
            print('UnicodeEncodeError: couldn\'t encode char {}'.format(i))

    # add 'next' item to the table
    # item_data = {'filter_proof': True}
    # ti = ci.TableItem(col_values=['', 'Show next page', ''], tag='next', hidden=False, action=next_page_action,
    #                   item_data=item_data)
    # tis.append(ti)

    ad = {'cat_filter': cat_filter, 'name_filter': name_filter}
    table = ci.Table(rows=tis, col_names=col_names, item_filter=unicode_item_filter, action_dict=ad, add_exit=False)
    ad['table'] = table
    return table

def make_key_binding(registry, table, table_buffer='DEFAULT_BUFFER'):
    tbl = table
    table_buffer = table_buffer

    @registry.add_binding(Keys.F2)
    def _(event):
        print('_F2_')
        cat_filter = ci.get_string(prompt="Category filter: ", default="**")
        name_filter = ci.get_string(prompt="Name filter: ", required=False)
        tbl.action_dict['cat_filter'] = cat_filter
        tbl.action_dict['name_filter'] = name_filter
        tbl.refresh_items(rows=tbl._table_items, add_exit=tbl.add_exit, item_filter=tbl.item_filter)
        if table_buffer:
            buffer = event.cli.buffers[table_buffer]
            buffer.text = tbl.table.get_string()
        raise ci.RefreshScreenInterrupt

    return registry

if __name__ == '__main__':
    # table = make_table(start=32, end=0x007F, cat_filter='**', name_filter='')
    # table = make_table(0x20A0,0x20CF)   # currency
    table = make_table(0x00080, 0x007FF, cat_filter='Ll', name_filter='')
    # result = ci.get_table_input(table)
    kr = make_key_binding(KeyBindingManager().registry, table)
    # kr = make_key_binding(default_key_registry, table)

    result = ci.get_table_input(table, key_registry=kr)
    # result = ci.get_table_input(table)
    print('char={}, result={}'.format(result[0], result))

    # display character