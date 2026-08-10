"""Tests for GetInput's option handling and retry behaviour.

The per-type convenience wrappers are covered by test_get_int / test_get_str and
friends. This file takes the options they do not exercise: retries, defaults,
hidden prompts, and the unknown-option warning.

Len Wanger, 2026
"""

import decimal
import logging

import pytest

from cooked_input import (
    DateConvertor,
    GetInput,
    IntConvertor,
    MaxRetriesError,
    RangeValidator,
    SimpleValidator,
    ValidationError,
    get_date,
    get_input,
    get_list,
    get_money,
    get_string,
    silent_error,
)


def _as_date(text):
    """Parse a date the same way get_date does, for building range bounds."""
    return DateConvertor()(text, silent_error, "{value}")


class TestRetries:
    def test_exhausting_the_retries_raises_max_retries_error(self, fake_input):
        feeder = fake_input("nope", "still nope")
        with pytest.raises(MaxRetriesError, match="Maximum retries exceeded"):
            get_input(convertor=IntConvertor(), retries=2, error_callback=silent_error)
        assert feeder.remaining == 0

    def test_a_good_value_before_the_limit_succeeds(self, fake_input):
        fake_input("nope", "42")
        assert get_input(convertor=IntConvertor(), retries=2, error_callback=silent_error) == 42

    def test_without_a_retry_limit_it_keeps_asking(self, fake_input):
        feeder = fake_input("a", "b", "c", "d", "42")
        assert get_input(convertor=IntConvertor(), error_callback=silent_error) == 42
        assert feeder.remaining == 0

    @pytest.mark.xfail(
        reason="#49: retries=0 never enters the loop, so `valid_response` is unbound "
               "and the caller gets UnboundLocalError instead of MaxRetriesError",
        strict=True,
    )
    def test_zero_retries_raises_max_retries_error(self, fake_input):
        fake_input("42")
        with pytest.raises(MaxRetriesError):
            get_input(retries=0)


class TestDefaults:
    def test_a_blank_entry_takes_the_default(self, fake_input):
        fake_input("")
        assert get_input(convertor=IntConvertor(), default="42") == 42

    def test_a_typed_value_beats_the_default(self, fake_input):
        fake_input("7")
        assert get_input(convertor=IntConvertor(), default="42") == 7

    def test_a_default_that_fails_validation_raises(self, fake_input):
        fake_input("")
        with pytest.raises(ValidationError, match="did not pass validation"):
            get_input(convertor=IntConvertor(), validators=RangeValidator(1, 10),
                      default="99", error_callback=silent_error)

    def test_the_default_is_shown_in_the_prompt(self, fake_input):
        feeder = fake_input("")
        get_input(convertor=IntConvertor(), default="42")
        assert " (enter for: 42)" in feeder.prompts[0]

    def test_a_custom_default_string_replaces_the_generated_one(self, fake_input):
        feeder = fake_input("")
        get_input(convertor=IntConvertor(), default="42", default_str="[the answer]")
        assert "[the answer]" in feeder.prompts[0]

    def test_an_optional_prompt_says_enter_to_leave_blank(self, fake_input):
        feeder = fake_input("")
        assert get_input(required=False) is None
        assert " (enter to leave blank)" in feeder.prompts[0]


class TestHiddenInput:
    def test_a_hidden_prompt_goes_through_getpass(self, fake_input):
        feeder = fake_input("secret")
        assert get_input(hidden=True) == "secret"
        # Proof it took the getpass branch rather than the visible one.
        assert len(feeder.hidden_prompts) == 1

    def test_a_hidden_default_is_masked_in_the_prompt(self, fake_input):
        # The point of masking: the default must not leak into the prompt text.
        feeder = fake_input("")
        assert get_input(hidden=True, default="hunter2") == "hunter2"
        assert " (enter for: ***)" in feeder.prompts[0]
        assert "hunter2" not in feeder.prompts[0]

    def test_a_visible_default_is_not_masked(self, fake_input):
        feeder = fake_input("")
        get_input(default="hunter2")
        assert "hunter2" in feeder.prompts[0]


class TestUnknownOptions:
    def test_an_unknown_option_is_logged_as_a_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            GetInput(bogus_option=1)

        assert "unknown option" in caplog.text
        assert "bogus_option" in caplog.text

    def test_an_unknown_option_does_not_stop_construction(self, fake_input, caplog):
        fake_input("42")
        with caplog.at_level(logging.WARNING):
            assert get_input(convertor=IntConvertor(), bogus_option=1) == 42


class TestGetListDefaults:
    def test_a_list_default_is_joined_for_display(self, fake_input):
        # Regression test: this used `collections.Iterable`, removed from the
        # collections namespace in Python 3.10, so any non-string iterable default
        # raised AttributeError on every supported version.
        feeder = fake_input("")
        assert get_list(default=["a", "b", "c"]) == ["a", "b", "c"]
        assert "a, b, c" in feeder.prompts[0]

    def test_a_string_default_is_used_as_written(self, fake_input):
        fake_input("")
        assert get_list(default="a,b") == ["a", "b"]

    def test_a_non_iterable_default_is_stringified(self, fake_input):
        fake_input("")
        assert get_list(default=42) == ["42"]

    def test_a_none_default_leaves_the_prompt_bare(self, fake_input):
        feeder = fake_input("x,y")
        assert get_list(default=None) == ["x", "y"]
        assert "enter for" not in feeder.prompts[0]


class TestRequiredAndBlank:
    def test_a_required_prompt_reprompts_on_blank(self, fake_input):
        # Blank input with required=True and no default matches no branch in the
        # retry loop, so `retries` never increments and get_input spins forever.
        # The feeder's EOFError is what turns that into a fast failure instead of
        # a hung test -- exactly the hang guard it exists for. Tracked in #44.
        fake_input("", "", "")
        with pytest.raises(EOFError):
            get_input(required=True)

    def test_a_required_prompt_accepts_a_real_value(self, fake_input):
        feeder = fake_input("something")
        assert get_input(required=True) == "something"
        assert feeder.remaining == 0

    def test_an_optional_prompt_returns_none_on_blank(self, fake_input):
        fake_input("")
        assert get_input(required=False) is None


class TestGetStringBounds:
    def test_min_len_rejects_a_short_string(self, fake_input):
        feeder = fake_input("ab", "abcd")
        assert get_string(min_len=3, error_callback=silent_error) == "abcd"
        assert feeder.remaining == 0

    def test_max_len_rejects_a_long_string(self, fake_input):
        fake_input("abcdef", "abc")
        assert get_string(max_len=3, error_callback=silent_error) == "abc"

    def test_both_bounds_together(self, fake_input):
        fake_input("a", "abcdef", "abc")
        assert get_string(min_len=2, max_len=4, error_callback=silent_error) == "abc"


class TestGetDateBounds:
    def test_a_date_inside_the_range_is_accepted(self, fake_input):
        fake_input("6/15/2020")
        result = get_date(minimum=_as_date("1/1/2020"), maximum=_as_date("12/31/2020"))
        assert result.year == 2020 and result.month == 6

    def test_a_date_before_the_minimum_is_rejected(self, fake_input):
        feeder = fake_input("1/1/2019", "6/15/2020")
        result = get_date(minimum=_as_date("1/1/2020"), error_callback=silent_error)
        assert result.year == 2020
        assert feeder.remaining == 0

    def test_a_date_after_the_maximum_is_rejected(self, fake_input):
        fake_input("6/15/2021", "6/15/2020")
        result = get_date(maximum=_as_date("12/31/2020"), error_callback=silent_error)
        assert result.year == 2020

    def test_a_caller_validator_is_combined_with_the_bounds(self, fake_input):
        # A single callable validator gets paired with the generated RangeValidator
        # rather than replacing it.
        not_june_first = SimpleValidator(lambda value: value.day != 1)
        fake_input("6/1/2020", "6/15/2020")
        result = get_date(minimum=_as_date("1/1/2020"), maximum=_as_date("12/31/2020"),
                          validators=not_june_first, error_callback=silent_error)
        assert result.day == 15

    def test_no_bounds_leaves_the_validators_alone(self, fake_input):
        fake_input("6/15/2020")
        assert get_date().year == 2020


class TestGetMoney:
    def test_a_dollar_symbol_is_stripped(self, fake_input):
        fake_input("$1234.56")
        assert get_money() == decimal.Decimal("1234.56")

    def test_thousands_separators_are_removed(self, fake_input):
        fake_input("$1,234,567.89")
        assert get_money() == decimal.Decimal("1234567.89")

    def test_a_non_dollar_symbol_is_stripped(self, fake_input):
        # The '$' branch needs a regex escape; anything else is used literally.
        fake_input("E1234.56")
        assert get_money(symbol="E") == decimal.Decimal("1234.56")

    def test_a_bare_number_needs_no_symbol(self, fake_input):
        fake_input("42")
        assert get_money() == decimal.Decimal("42")

    def test_a_custom_separator_is_honoured(self, fake_input):
        fake_input("$1.234.567")
        assert get_money(separator=".") == decimal.Decimal("1234567")

    def test_the_default_prompt_mentions_money(self, fake_input):
        feeder = fake_input("42")
        get_money()
        assert "amount of money" in feeder.prompts[0]

    def test_a_caller_prompt_wins(self, fake_input):
        feeder = fake_input("42")
        get_money(prompt="How much?")
        assert "How much?" in feeder.prompts[0]
