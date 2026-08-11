
"""
pytest tests for cooked_input cleaning functions

Len Wanger, 2017
"""

import pytest
import re


from pytest import approx

from cooked_input import get_input
from cooked_input import Cleaner, StripCleaner, CapitalizationCleaner, RemoveCleaner, ReplaceCleaner, RegexCleaner, ChoiceCleaner


class TestCleaners(object):

    def test_the_base_cleaner_cannot_be_instantiated(self):
        # Regression guard for #50: Cleaner used to declare `__metaclass__ = ABCMeta`, the
        # Python 2 spelling, which is inert on Python 3 -- so the "abstract" base was
        # instantiable and its __call__ silently returned None.
        with pytest.raises(TypeError, match="abstract"):
            Cleaner()

    def test_a_subclass_implementing_call_alone_is_concrete(self):
        # __init__ is deliberately not abstract, so this common shape keeps working.
        class ShoutCleaner(Cleaner):
            def __call__(self, value):
                return value.upper()

        assert ShoutCleaner()("quiet") == "QUIET"

    def test_a_subclass_without_call_cannot_be_instantiated(self):
        class ForgetfulCleaner(Cleaner):
            pass

        with pytest.raises(TypeError, match="abstract"):
            ForgetfulCleaner()

    def test_bad_cleaner(self, fake_input):
        input_str = 'foo'
        with pytest.raises(RuntimeError):
            fake_input(input_str)
            # Not a cleaner and not iterable, which is what compose rejects.
            result = get_input(cleaners=10)  # ty: ignore[invalid-argument-type]

    def test_strip_cleaner(self, fake_input):
        input_str = '  \t foo  \nf'
        sc = StripCleaner(lstrip=True, rstrip=True)
        fake_input(input_str)
        result = get_input(cleaners=sc)
        assert (result == 'foo')

        assert repr(sc) == 'StripCleaner(lstrip=True, rstrip=True)'

    def test_every_cap_style_constant_is_exported(self):
        # LAST_WORD_CAP_STYLE used to be the one style missing from the package's
        # __init__, so ci.LAST_WORD_CAP_STYLE raised AttributeError while the
        # equivalent 'last_word' string worked. Assert the whole set, not just the
        # one that was broken, so the next addition cannot be forgotten either.
        import cooked_input as ci

        exported = {
            'lower': ci.LOWER_CAP_STYLE,
            'upper': ci.UPPER_CAP_STYLE,
            'first_word': ci.FIRST_WORD_CAP_STYLE,
            'last_word': ci.LAST_WORD_CAP_STYLE,
            'all_words': ci.ALL_WORDS_CAP_STYLE,
        }
        for style_str, style_const in exported.items():
            assert CapitalizationCleaner(style=style_str)._style == style_const

    def test_capitalization_cleaner(self, fake_input):
        input_str = 'foo Bar bLaT'
        sc = CapitalizationCleaner(style='lower')
        fake_input(input_str)
        result = get_input(cleaners=sc)
        assert (result == 'foo bar blat')

        assert repr(sc) == 'CapitalizationCleaner(style=1)'

        sc = CapitalizationCleaner(style='upper')
        fake_input(input_str)
        result = get_input(cleaners=sc)
        assert (result == 'FOO BAR BLAT')

        sc = CapitalizationCleaner(style='first_word')
        fake_input(input_str)
        result = get_input(cleaners=sc)
        assert (result == 'Foo bar blat')

        sc = CapitalizationCleaner(style='all_words')
        fake_input(input_str)
        result = get_input(cleaners=sc)
        assert (result == 'Foo Bar Blat')

        sc = CapitalizationCleaner(style='last_word')
        fake_input(input_str)
        result = get_input(cleaners=sc)
        assert (result == 'foo bar Blat')

        with pytest.raises(ValueError):
            sc = CapitalizationCleaner(style=6)

        with pytest.raises(ValueError):
            sc = CapitalizationCleaner(style='bad_style')


    def test_remove_cleaner(self, fake_input):
        input_str = 'foo is bar'
        rc = RemoveCleaner(patterns=['is', u'bar'])
        fake_input(input_str)
        result = get_input(cleaners=rc)
        assert(result == 'foo  ')

        assert repr(rc) == "RemoveCleaner(patterns=['is', 'bar'])"

        # A non-string pattern is the point: str.replace rejects it at call time, which
        # is why the construction sits outside the raises block.
        rc = RemoveCleaner(patterns=['is', 10])  # ty: ignore[invalid-argument-type]
        with pytest.raises(TypeError):
            fake_input(input_str)
            result = get_input(cleaners=rc)

    def test_replace_cleaner(self, fake_input):
        input_str = 'foo and bar and blat'
        rc = ReplaceCleaner(old='and', new='&')
        fake_input(input_str)
        result = get_input(cleaners=rc)
        assert(result == 'foo & bar & blat')

        assert repr(rc) == 'ReplaceCleaner(old="and", new="&")'

        input_str = 'foo and bar and blat'
        rc = ReplaceCleaner(old='and', new='&', count=1)
        fake_input(input_str)
        result = get_input(cleaners=rc)
        assert (result == 'foo & bar and blat')

        with pytest.raises(TypeError):
            # The bad keyword is the point of the test, so the type error is expected.
            rc = ReplaceCleaner(old='and', new='&', bad_option='foo')  # ty: ignore[unknown-argument]


    def test_regex_cleaner(self, fake_input):
        input_str = 'foo and bar'
        rc = RegexCleaner(pattern=r'\sAND\s', repl=' & ', flags=re.IGNORECASE)
        fake_input(input_str)
        result = get_input(cleaners=rc)
        assert(result == 'foo & bar')

        assert repr(rc) == 'RegexCleaner(pattern=\\sAND\\s, repl= & , count=0, flags=re.IGNORECASE)'


    def test_choice_cleaner(self, fake_input):
        input_str = 'bar\nf'
        color_choices = ['foo']
        cc = ChoiceCleaner(color_choices)
        fake_input(input_str)
        result = get_input(cleaners=cc)
        assert(result == 'bar')
        result = get_input(cleaners=cc)
        assert (result == 'foo')

        assert repr(cc) == "ChoiceCleaner(choices={'foo': 'foo'})"

    def test_subset_choice(self, fake_input):
        # make sure works if one value is a subset of another and case insenstive
        input_str = 'date'

        type_choices = ['Boolean', 'Date', 'DateTime']
        ft_cleaner = ChoiceCleaner(type_choices, case_sensitive=False)

        fake_input(input_str)
        result = get_input(prompt="Type", cleaners=ft_cleaner)
        assert (result == 'Date')

    def test_case_isensitive_choice_cleaner(self, fake_input):
        input_str = 'b\nbl\nBL\nf'
        color_choices = ['foo', 'bar', 'BLAT']
        cc = ChoiceCleaner(color_choices, case_sensitive=False)
        fake_input(input_str)
        result = get_input(cleaners=cc)
        assert(result == 'b')
        result = get_input(cleaners=cc)
        assert (result == 'BLAT')
        result = get_input(cleaners=cc)
        assert (result == 'BLAT')
        result = get_input(cleaners=cc)
        assert (result == 'foo')

        assert repr(cc) == "ChoiceCleaner(choices={'foo': 'foo', 'bar': 'bar', 'blat': 'BLAT'})"


    def test_case_sesitive_choice_cleaner(self, fake_input):
        input_str = 'b\nbl\nBL\nf'
        color_choices = ['foo', 'bar', 'BLAT']
        cc = ChoiceCleaner(color_choices, case_sensitive=True)
        fake_input(input_str)
        result = get_input(cleaners=cc)
        assert (result == 'bar')
        result = get_input(cleaners=cc)
        assert (result == 'bl')
        result = get_input(cleaners=cc)
        assert (result == 'BLAT')
        result = get_input(cleaners=cc)
        assert (result == 'foo')

        assert repr(cc) == "ChoiceCleaner(choices={'foo': 'foo', 'bar': 'bar', 'BLAT': 'BLAT'})"

    def test_subset_choice_cleaner(self, fake_input):
        # test choice cleaner if one of the choices is the subset of another
        input_str = 'foo\nf\nfoob'
        color_choices = ['foo', 'foobar']
        cc = ChoiceCleaner(color_choices)
        fake_input(input_str)
        result = get_input(cleaners=cc)
        assert(result == 'foo')
        result = get_input(cleaners=cc)
        assert (result == 'f')
        result = get_input(cleaners=cc)
        assert (result == 'foobar')
        assert repr(cc) == "ChoiceCleaner(choices={'foo': 'foo', 'foobar': 'foobar'})"
