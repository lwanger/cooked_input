"""Tests for the last few uncovered branches across the package.

These are the leftovers the topic-focused test files do not naturally reach:
alternate cleaner configurations, the list-plus-generated-validator paths in the
get_* convenience functions, and a couple of repr and message branches.

Len Wanger, 2026
"""

import decimal

import pytest

from cooked_input import (
    ChoiceConvertor,
    DEFAULT_VALIDATOR_ERROR,
    LengthValidator,
    RangeValidator,
    RegexValidator,
    RemoveCleaner,
    StripCleaner,
    SimpleValidator,
    get_date,
    get_list,
    get_money,
    get_string,
    print_error,
    silent_error,
)
from cooked_input.validators import in_all, in_any


class TestStripCleanerSides:
    @pytest.mark.parametrize("lstrip, rstrip, expected", [
        (True, True, "x"),
        (True, False, "x  "),
        (False, True, "  x"),
        (False, False, "  x  "),
    ])
    def test_each_combination_of_sides(self, lstrip, rstrip, expected):
        assert StripCleaner(lstrip=lstrip, rstrip=rstrip)("  x  ") == expected


class TestRemoveCleanerCount:
    def test_every_occurrence_is_removed_by_default(self):
        assert RemoveCleaner(["a"])("banana") == "bnn"

    def test_a_count_limits_how_many_are_removed(self):
        assert RemoveCleaner(["a"], count=2)("banana") == "bnna"

    def test_several_patterns_are_applied_in_turn(self):
        assert RemoveCleaner(["a", "n"])("banana") == "b"


class TestBareValuesInsideValidatorLists:
    def test_in_any_falls_back_to_equality_for_a_non_callable(self):
        # The earlier validator has to fail first, or in_any short-circuits before
        # ever reaching the bare value.
        assert in_any(99, [RangeValidator(1, 10), 99], silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_in_any_reports_failure_when_the_bare_value_differs(self):
        assert in_any(99, [RangeValidator(1, 10), 5], silent_error, DEFAULT_VALIDATOR_ERROR) is False

    def test_in_all_cannot_take_a_bare_value_in_a_list(self):
        # Characterization of an asymmetry: in_any and not_in both fall back to an
        # equality test for a non-callable list entry, but in_all calls every entry
        # unconditionally, so a bare value raises TypeError instead.
        with pytest.raises(TypeError):
            in_all(5, [RangeValidator(1, 10), 5], silent_error, DEFAULT_VALIDATOR_ERROR)


class TestRegexValidatorMessages:
    def test_a_description_equal_to_the_pattern_reports_the_pattern(self, capsys):
        # When regex_desc is the pattern itself there is no friendly name to use,
        # so the message quotes the pattern instead.
        pattern = r"^\d{7}$"
        RegexValidator(pattern, regex_desc=pattern)("nope", print_error, DEFAULT_VALIDATOR_ERROR)
        assert "does not match pattern" in capsys.readouterr().err


class TestChoiceConvertorRepr:
    def test_repr_names_the_choices(self):
        assert repr(ChoiceConvertor({"a": 1})) == \
            "ChoiceConvertor(choices={'a': 1}, value_error_str=a valid row number)"


class TestGetStringWithValidatorList:
    def test_a_length_bound_is_appended_to_a_validator_list(self, fake_input):
        # min_len/max_len build a LengthValidator that has to be combined with
        # whatever the caller already passed.
        no_digits = SimpleValidator(lambda value: not any(c.isdigit() for c in value))
        feeder = fake_input("ab1cd", "ab", "abcd")
        result = get_string(validators=[no_digits], min_len=3, error_callback=silent_error)
        assert result == "abcd"
        assert feeder.remaining == 0

    def test_a_single_validator_is_combined_too(self, fake_input):
        no_digits = SimpleValidator(lambda value: not any(c.isdigit() for c in value))
        fake_input("ab", "abcd")
        assert get_string(validators=no_digits, min_len=3, error_callback=silent_error) == "abcd"


class TestGetDateWithValidatorList:
    def test_a_range_is_appended_to_a_validator_list(self, fake_input):
        not_the_first = SimpleValidator(lambda value: value.day != 1)
        minimum = get_date.__globals__["DateConvertor"]()("1/1/2020", silent_error, "{value}")
        fake_input("6/1/2020", "6/15/2020")
        result = get_date(validators=[not_the_first], minimum=minimum,
                          error_callback=silent_error)
        assert result.day == 15


class TestGetMoneyDecimalOptions:
    def test_precision_is_forwarded_to_the_convertor(self, fake_input):
        fake_input("$1.23")
        assert get_money(precision=4) == decimal.Decimal("1.23")

    def test_rounding_is_forwarded_to_the_convertor(self, fake_input):
        fake_input("$1.23")
        assert get_money(rounding="ROUND_DOWN") == decimal.Decimal("1.23")

    def test_precision_two_gives_whole_cents(self, fake_input):
        # The point of #48 from a caller's seat: this used to return 1234.567 whatever
        # precision and rounding were set to.
        fake_input("$1,234.567")
        assert get_money(precision=2) == decimal.Decimal("1234.57")

    def test_rounding_changes_the_cents(self, fake_input):
        fake_input("$1,234.567")
        assert get_money(precision=2, rounding="ROUND_DOWN") == decimal.Decimal("1234.56")


class TestGetListErrorOptions:
    def test_an_error_callback_is_forwarded_into_the_list_convertor(self, fake_input):
        received = []

        def record(fmt_str, value, error_content):
            received.append(value)

        fake_input("a,b")
        get_list(error_callback=record)
        assert received == []  # nothing failed, but the option was accepted

    def test_a_validator_error_format_is_accepted(self, fake_input):
        feeder = fake_input("a,b,c")
        assert get_list(validator_error_fmt="bad: {value}") == ["a", "b", "c"]
        assert feeder.remaining == 0
