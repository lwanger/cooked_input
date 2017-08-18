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
    # make lower case
    def __init__(self, **kwargs):
        super(LowerCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value.lower()
        return result

    def __repr__(self):
        return 'LowerCleaner()'


class UpperCleaner(Cleaner):
    # make upper case
    def __init__(self, **kwargs):
        super(UpperCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value.upper()
        return result

    def __repr__(self):
        return 'UpperCleaner()'


class CapitalizeCleaner(Cleaner):
    # capitalize the input
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
    # strip off white space
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
    # Replace the find_str with the replace_str
    def __init__(self, old, new, **kwargs):
        self._old = old
        self._new = new
        # TODO - add an option count keyword arg?
        super(LowerCleaner, self).__init__(**kwargs)

    def __call__(self, value):
        result = value.replace(self._old, self._new)
        return result

    def __repr__(self):
        return 'ReplaceCleaner()'
