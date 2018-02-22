"""
This file contains cleaner classes for cooked_input

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import re
import logging
from string import capwords
from .input_utils import put_in_a_list, cap_last_word

LOWER_CAP_STYLE = 1
UPPER_CAP_STYLE = 2
FIRST_WORD_CAP_STYLE = 3
LAST_WORD_CAP_STYLE = 4
ALL_WORDS_CAP_STYLE = 5

# CAP_STYLES = { LOWER_CAP_STYLE, UPPER_CAP_STYLE, FIRST_WORD_CAP_STYLE, ALL_WORDS_CAP_STYLE }
CAP_STYLES = { LOWER_CAP_STYLE, UPPER_CAP_STYLE, FIRST_WORD_CAP_STYLE, LAST_WORD_CAP_STYLE, ALL_WORDS_CAP_STYLE }

CAP_STYLE_STRS = {
    'lower': LOWER_CAP_STYLE,
    'upper': UPPER_CAP_STYLE,
    'first_word': FIRST_WORD_CAP_STYLE,
    'capitalize': FIRST_WORD_CAP_STYLE,
    'last_word': LAST_WORD_CAP_STYLE,
    'all_words': ALL_WORDS_CAP_STYLE,
    'capwords': ALL_WORDS_CAP_STYLE
}


###
### Cleaners:
###
# class Cleaner(metaclass=ABCMeta):
class Cleaner(object):
    # Abstract base class for cleaner classes
    def __init__(self):
        pass

    # @abstractmethod
    def __call__(self, value):
        pass


class CapitalizationCleaner(Cleaner):
    """
    Capitalize the value using the specified style

    :param style: capitalization style to use: 'lower', 'upper', 'first_word', 'last_word'[#f1]_, 'all_words'.

.. [#f1] This parameter is dedicated to Colleen, who will be happy to finally get the last word.

The styles are equivalent to the following:

    +--------------+-----------------+----------------------------------------------------+
    | style        | string function |                       Note                         |
    +--------------+-----------------+----------------------------------------------------+
    | 'lower'      | lower           |  can also use LOWER_CAP_STYLE                      |
    +--------------+-----------------+----------------------------------------------------+
    | 'upper'      | upper           |  can also use UPPER_CAP_STYLE                      |
    +--------------+-----------------+----------------------------------------------------+
    | 'first_word' | capitalize      |  can also use 'capitalize' or FIRST_WORD_CAP_STYLE |
    +--------------+-----------------+----------------------------------------------------+
    | 'last_word'  | --              |  can also use  LAST_WORD_CAP_STYLE                 |
    +--------------+-----------------+----------------------------------------------------+
    | 'all_words'  | capwords        |  can also use 'capwords' or ALL_WORDS_CAP_STYLE    |
    +--------------+-----------------+----------------------------------------------------+

    """
    def __init__(self, style='lower', **kwargs):
        if isinstance(style, int):
            if style in CAP_STYLES:
                self._style = style
            else:
                raise ValueError('CapitalizationCleaner: {} is not a valid capitalization style'.format(style))
        else:   # a string type
            if style in CAP_STYLE_STRS:
                self._style = CAP_STYLE_STRS[style]
            else:
                raise ValueError('CapitalizationCleaner: {} is not a valid capitalization style'.format(style))

        super(CapitalizationCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        if self._style == LOWER_CAP_STYLE:
            return value.lower()
        elif self._style == UPPER_CAP_STYLE:
            return value.upper()
        elif self._style == FIRST_WORD_CAP_STYLE:
            return value.capitalize()
        elif self._style == LAST_WORD_CAP_STYLE:
            return cap_last_word(value)
        else:    # ALL_WORDS_CAP_STYLE:
            return capwords(value)

    def __repr__(self):
        return 'CapitalizationCleaner(style={})'.format(self._style)


class StripCleaner(Cleaner):
    """
    Strips white space from the input value. Strips from the left side if lstrip=True, and from the
    right side if rstrip=True. Both are True by default (i.e. strips from left and right).

    :param lstrip: strips white space from the left side of the value if True
    :param rstrip: strips white space from the right side of the value if True
    """
    def __init__(self, lstrip=True, rstrip=True, **kwargs):
        self._lstrip = lstrip
        self._rstrip = rstrip
        super(StripCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value
        if self._lstrip:
            result = result.lstrip()
        if self._rstrip:
            result = result.rstrip()
        return result

    def __repr__(self):
        return 'StripCleaner(lstrip=%r, rstrip=%s)' % (self._lstrip, self._rstrip)


class ChoiceCleaner(Cleaner):
    """
    ChoiceCleaner tries to replace the input value with a single element from a list of choices by finding the unique
    element starting with the input value. If not single element can be identified, the input value is returned (i.e. no
    cleaning is performed.) This is a complicated way of saying you can type in the first few letters of an input and
    the cleaner will return the choice that starts with those letters if it can determine which one it is.

    For example::

        ChoiceCleaner(choices=['blue', 'black', 'brown', 'green'])

    will with the following input values would return the following values:

        +-------+---------+-----------------------------------------------------------------+
        | value | returns |                              Note                               |
        +-------+---------+-----------------------------------------------------------------+
        | 'g'   | 'green' |                                                                 |
        +-------+---------+-----------------------------------------------------------------+
        | 'br'  | 'brown' |                                                                 |
        +-------+---------+-----------------------------------------------------------------+
        | 'blu' | 'blue'  |                                                                 |
        +-------+---------+-----------------------------------------------------------------+
        | 'bl'  | 'bl'    | original value returned as can't tell between 'black' and 'blue'|
        +-------+---------+-----------------------------------------------------------------+

    :param choices: a list of to detect
    """
    def __init__(self, choices, case_insensitive=False, **kwargs):
        """
        Return the choice starting with the value.

        :param choices: the list of choices to identify
        :param case_insensitive: matching the choice is case sensitive if True (default) or insensitive if False.
        :param kwargs:
        """

        self._case_insensitive = case_insensitive

        # create a dictionary as choices may not be strings
        if case_insensitive:
            self._str_choices = {str(choice).lower(): choice for choice in choices}
        else:
            self._str_choices = {str(choice): choice for choice in choices}

        super(ChoiceCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        if self._case_insensitive:
            str_value = str(value).lower()
        else:
            str_value = str(value)
        matches = [v for k, v in self._str_choices.items() if k.startswith(str_value)]

        if len(matches) == 1:
            return matches[0]
        else:
            return value

    def __repr__(self):
        return 'ChoiceCleaner(choices={})'.format(self._str_choices)


class RemoveCleaner(Cleaner):
    """
    Removes all occurrences of any of the strings in the patterns list.

    :param patterns: string to replace

    """
    def __init__(self, patterns, **kwargs):
        self._patterns = put_in_a_list(patterns)
        super(RemoveCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value
        for pattern in self._patterns:
            result = result.replace(pattern, '')

        return result

    def __repr__(self):
        return 'ReplaceCleaner(patterns={})'.format(self._patterns)


class ReplaceCleaner(Cleaner):
    """
    Replaces all occurrences of "old" string with "new" string white space from the input value

    :param old: string to replace
    :param new: string to put in the place of all occurrences of old

    options:

    count: the maximum number of substitutions to perform to the value.
    """
    def __init__(self, old, new, **kwargs):
        count = None

        for k, v in kwargs.items():
            if k == 'count':
                count = v
            else:
                logging.warning('Warning: ReplaceCleaner received unknown option (%s)' % k)

        self._old = str(old)
        self._new = str(new)
        self._count = count

        super_options_to_skip = {'count'}
        super_kwargs = {k: v for k, v in kwargs.items() if k not in super_options_to_skip}

        super(ReplaceCleaner, self).__init__(**super_kwargs)

    def __call__(self, value):
        if self._count is None:
            result = value.replace(self._old, self._new)
        else:
            result = value.replace(self._old, self._new, self._count)

        return result

    def __repr__(self):
        return 'ReplaceCleaner(old="{}", new="{}")'.format(self._old, self._new)


class RegexCleaner(Cleaner):
    """
    Return the result of substituting the sub value for the pattern using a regular expression on the value. For more
    information on regular expressions and the meaning of count and flags.See the Python re module
    in the standard library at:

        https://docs.python.org/2/library/re.html

    :param pattern: regular expression to search for
    :param sub: regular expression to substitute for the pattern
    :param count: count
    :param flags: flags
    """
    def __init__(self, pattern, sub, count=0, flags=0, **kwargs):
        self._pattern = pattern
        self._sub = sub
        self._count = count
        self._flags = flags
        super(RegexCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = re.sub(self._pattern, self._sub, value, self._count, self._flags)
        return result

    def __repr__(self):
        return 'RegexCleaner(pattern={}, sub={}, count={}, flags={})'.format(self._pattern, self._sub, self._count, self._flags)
