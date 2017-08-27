
"""
get_input module to get values from the command line.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
import collections
import prettytable


def compose(value, funcs):
    """
    Compose functions and return the result: compose(value, [f1,f2,f3]) = f3(f2(f1(value)))

    :param value: the value to apply to funcs (the composed list of functions.)
    :param funcs: a function or list of functions to compose.

    :return: the return value of the functions composed together.
    """
    first_func = True
    result = None

    if callable(funcs):
        result = funcs(value)
    elif isinstance(funcs, collections.Iterable):
        for func in funcs:
            if first_func:
                result = func(value)
                first_func = False
            else:
                result = func(result)
    else:
        raise RuntimeError('funcs cannot be called')

    return result


def make_pretty_table(rows, second_col_name='name', sort_by_second_col=True):
    """
    Take a list of tuples [(id, value), ...] and return a prettytable

    :param rows: a list of tuples for the table rows. Each tuple is: (id, value).
    :param second_col_name: the name to use for the header on the second column.
    :param sort_by_second_col: sort by the second column if True, otherwise leave in order from rows.
    :return: a prettytable for the table.
    """
    x = prettytable.PrettyTable(['id', second_col_name])

    for row in rows:
        x.add_row([row[0], row[1]])

    x.align[second_col_name] = 'l'  # left align
    x.sortby = second_col_name if sort_by_second_col else 'id'
    return x


def put_in_a_list(values):
    """
    An annoyance in Pythons is you can't easily tell between an iterable (e.g. a list) and a string (i.e. both are
    iterables.) This is a pain if you try to create a list of these things as list('foo') returns ['f', 'o'. 'o'].
    There are also a bunch of cases to take into account now (strings, bytes, unicode, legacy Python) too.
    This routine takes either a single value or list of values and returns a list of those values.

    :param values:
    :return: list containing the values
    """

    if values is None:
        result = []
    elif sys.version_info[0] < 3 and isinstance(values, unicode):  # For Python 2 - unicode is different than strings
        result = [values]
    elif sys.version_info[0] > 2 and isinstance(values, bytes):  # For Python 3 - check for bytes
        result = [values]
    elif isinstance(values, str):
        result = [values]
    elif isinstance(values, collections.Iterable):  # list or other iterable
        result = list(values)
    else:  # single non-iterable value
        result = [values]

    return result
