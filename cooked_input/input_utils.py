
"""
get_input module to get values from the command line.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""

from __future__ import annotations

import prettytable

from collections.abc import Iterable, Iterator, Sequence
from typing import Any, Callable, TypeVar

#: Element type of the sequence handed to :func:`renumerate`, so that the yielded items
#: keep whatever type went in rather than degrading to ``Any``.
_Element = TypeVar('_Element')


def compose(value: Any, funcs: Callable[[Any], Any] | Iterable[Callable[[Any], Any]]) -> Any:
    """
    Compose functions and return the result: compose(value, [f1,f2,f3]) = f3(f2(f1(value)))

    :param value: the value to apply to funcs (the composed list of functions.)
    :param funcs: a function or list of functions to compose.

    :return: the return value of the functions composed together. Composing an empty
      list of functions is the identity -- the value comes back unchanged.
    """
    first_func = True
    # Fixing: this used to be `result = None`, which was returned as-is when `funcs`
    # was empty, so composing nothing destroyed the value instead of passing it through.
    result = value

    if callable(funcs):
        # An object can be both callable and iterable, so narrowing on callable() alone
        # leaves a callable of unknown signature rather than the one-argument function
        # this branch is for. Testing the two in the other order would resolve that but
        # would also change which branch such an object takes, so the check stays put.
        result = funcs(value)  # ty: ignore[call-top-callable]
    elif isinstance(funcs, Iterable):
        for func in funcs:
            if first_func:
                result = func(value)
                first_func = False
            else:
                result = func(result)
    else:
        raise RuntimeError('funcs cannot be called')

    return result


def make_pretty_table(rows: Iterable[Sequence[Any]], second_col_name: str = 'name',
                      sort_by_second_col: bool = True) -> prettytable.PrettyTable:
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


def isstring(s: Any) -> bool:
    """
    An annoyance in Pythons is you can't easily tell something is a string-like thing (string, bytes, etc.)
    For instance, both 'abc' and ['a', 'b', 'c'] are iterators, but the latter is not a valid password! Further, in
    some cases strings can be of type bytes, which is not caught as a str. This function checks if the value can be
    treated like a string.

    :param s: the value to check
    :return: True if value is a string-like thing (string, bytes, etc.), otherwise False
    """
    return isinstance(s, (str, bytes))


def put_in_a_list(values: Any) -> list[Any]:
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
    elif isstring(values):
        result = [values]
    elif isinstance(values, Iterable):  # list or other iterable
        result = list(values)
    else:  # single non-iterable value
        result = [values]

    return result


def renumerate(sequence: Sequence[_Element]) -> Iterator[tuple[int, _Element]]:
    """
    Reverse emumerate - starts at the highest index (last item in the iterator) and counts down. This generator yields
    a tuple containing the index and item, starting with the last item in the iterator.

    Don't use reversed(list(enumerate(sequence))) as it's not efficient (it has to iterate through the whole sequence first.)

    :param sequence:
    :return:
    """
    for i in range(len(sequence)-1, -1, -1):
        yield (i, sequence[i])


def swap_element(sequence: Any, idx: int, replacement: Any) -> Any:
    """
    Returns a copy of the sequence with the ith value swapped with the replacement value. Useful for immutable values
    such as strings.

    :param sequence: the original immutable sequence.
    :param idx: the index of the sequence element to swap (use negative index to count from last element of the sequence.)
    :param replacement: the replacement value the ith element of the sequence

    :return: a copy of the original sequence with the ith element replaced by the replacement value
    """
    seq_length = len(sequence)

    if seq_length == 0: # return a copy of the empty sequence
        raise ValueError('cannot swap value in an empty sequence')

    if idx < 0:
        use_idx = seq_length + idx
    else:
        use_idx = idx

    if use_idx < 0 or use_idx >= seq_length:
        raise IndexError('index out of range')

    if seq_length == 1: # swap element in a single element sequence
        return replacement
    elif use_idx == 0:  # swap first element
        return replacement + sequence[1:]
    elif use_idx == seq_length-1:   # swap last element
        return sequence[:use_idx] + replacement
    else:   # swap an element in the middle of a sequence
        return sequence[:use_idx] + replacement + sequence[use_idx + 1:]


def cap_last_word(value: str) -> str:
    """
    Capitalize the last word of a string.

    :param value: string to capitalize

    :return: a copy of the string with the last word capitalized.
    """
    last_non_white_char = None

    for i,c in renumerate(value):
        if not c.isspace(): # last_non_white_space = i
            last_non_white_char = c
            continue
        elif last_non_white_char is not None and c.isspace():
            result = value.lower()
            result = swap_element(result, i+1, last_non_white_char.upper())
            return result

    if last_non_white_char is None: # value is all white space, return the original value
        return  value

    # String does not have any white space, so first word is the last word
    return value.capitalize()
