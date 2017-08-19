"""
get_input module to get values from the command line.

This file contains cleaner classes for io_get_input

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
from string import capwords


####
#### Cleaners:
####
# class Cleaner(metaclass=ABCMeta):
class Cleaner(object):
    # Abstract base class for cleaner classes
    def __init__(self):
        pass

    # @abstractmethod
    def __call__(self, value):
        pass


class LowerCleaner(Cleaner):
    """
    Make the value all lower case.
    """
    def __init__(self, **kwargs):
        super(LowerCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value.lower()
        return result

    def __repr__(self):
        return 'LowerCleaner()'


class UpperCleaner(Cleaner):
    """
    Make the value all upper case.
    """
    def __init__(self, **kwargs):
        super(UpperCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value.upper()
        return result

    def __repr__(self):
        return 'UpperCleaner()'


class CapitalizeCleaner(Cleaner):
    """
    Capitalize the value all upper case.

    :param all_words: capitalize all of the words of the value if True, only capitalize the first word if False (default).
    """
    def __init__(self, all_words=False, **kwargs):
        """
        Capitalize the value

        :param all_words: capitalize all of the words of the value if True, if False, only capitalize the first word.
        :param kwargs:
        """
        self.all_words = all_words
        super(CapitalizeCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        if self.all_words:
            result = value.capitalize()
        else:
            result = capwords(value)

        return result

    def __repr__(self):
        return 'CapitalizeCleaner(all_words={})'.format(self.all_words)


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


class ReplaceCleaner(Cleaner):
    """
    Replaces all occurances of "old" string with "new" string white space from the input value

    :param old: string to replace
    :param new: string to put in the place of all occurances of old
    """
    def __init__(self, old, new, **kwargs):
        self._old = old
        self._new = new
        # TODO - add an option count keyword arg?
        super(ReplaceCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value.replace(self._old, self._new)
        return result

    def __repr__(self):
        return 'ReplaceCleaner()'
