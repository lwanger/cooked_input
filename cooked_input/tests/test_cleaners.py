
"""
pytest tests for cooked_input cleaning functions

Len Wanger, 2017
"""

import sys
import pytest
import re

if sys.version_info[0] > 2:  # For Python 3
    from io import StringIO
else:
    from StringIO import StringIO

from pytest import approx

from cooked_input import get_input
from cooked_input import Cleaner, StripCleaner, CapitalizationCleaner, RemoveCleaner, ReplaceCleaner, RegexCleaner, ChoiceCleaner
from .utils import redirect_stdin


class TestGetFloat(object):

    def test_call_abstract(self):
        c = Cleaner()
        c(10)

    def test_bad_cleaner(self):
        input_str = 'foo'
        with pytest.raises(RuntimeError):
            with redirect_stdin(StringIO(input_str)):
                result = get_input(cleaners=10)

    def test_strip_cleaner(self):
        input_str = '  \t foo  \nf'
        sc = StripCleaner(lstrip=True, rstrip=True)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=sc)
            assert (result == 'foo')

        print(sc)

    def test_capitalization_cleaner(self):
        input_str = 'foo Bar bLaT'
        sc = CapitalizationCleaner(style='lower')
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=sc)
            assert (result == 'foo bar blat')

        print(sc)

        sc = CapitalizationCleaner(style='upper')
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=sc)
            assert (result == 'FOO BAR BLAT')

        sc = CapitalizationCleaner(style='first_word')
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=sc)
            assert (result == 'Foo bar blat')

        sc = CapitalizationCleaner(style='all_words')
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=sc)
            assert (result == 'Foo Bar Blat')

        sc = CapitalizationCleaner(style='last_word')
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=sc)
            assert (result == 'foo bar Blat')

        with pytest.raises(ValueError):
            sc = CapitalizationCleaner(style=6)

        with pytest.raises(ValueError):
            sc = CapitalizationCleaner(style='bad_style')


    def test_remove_cleaner(self):
        input_str = 'foo is bar'
        rc = RemoveCleaner(patterns=['is', u'bar'])
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=rc)
            assert(result == 'foo  ')

        print(rc)

        rc = RemoveCleaner(patterns=['is', 10])
        with pytest.raises(TypeError):
            with redirect_stdin(StringIO(input_str)):
                result = get_input(cleaners=rc)

    def test_replace_cleaner(self):
        input_str = 'foo and bar and blat'
        rc = ReplaceCleaner(old='and', new='&')
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=rc)
            assert(result == 'foo & bar & blat')

        print(rc)

        input_str = 'foo and bar and blat'
        rc = ReplaceCleaner(old='and', new='&', count=1)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=rc)
            assert (result == 'foo & bar and blat')

        with pytest.raises(TypeError):
            rc = ReplaceCleaner(old='and', new='&', bad_option='foo')


    def test_regex_cleaner(self):
        input_str = 'foo and bar'
        rc = RegexCleaner(pattern=r'\sAND\s', sub=' & ', flags=re.IGNORECASE)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=rc)
            assert(result == 'foo & bar')

        print(rc)


    def test_choice_cleaner(self):
        input_str = 'bar\nf'
        color_choices = ['foo']
        cc = ChoiceCleaner(color_choices)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=cc)
            assert(result == 'bar')
            result = get_input(cleaners=cc)
            assert (result == 'foo')

        print(cc)
