"""Tests for the module-level process_value and the convertors test_convertors misses.

``process_value`` is the pure-function half of ``GetInput``: it runs the clean ->
convert -> validate pipeline against a value you already have, with no console
involved. It had no coverage at all.

Len Wanger, 2026
"""

import decimal

import pytest

from cooked_input import (
    BooleanConvertor,
    ChoiceConvertor,
    ChoiceValidator,
    ConvertorError,
    DecimalConvertor,
    IntConvertor,
    LengthValidator,
    ListConvertor,
    RangeValidator,
    StripCleaner,
    CapitalizationCleaner,
    process_value,
    silent_error,
)


def convert(convertor, value):
    """Run a convertor with the noisy arguments filled in."""
    return convertor(value, silent_error, "{value}")


class TestProcessValue:
    def test_a_clean_value_passes_straight_through(self):
        assert process_value("42", convertor=IntConvertor()) == (True, 42)

    def test_cleaners_run_before_the_convertor(self):
        assert process_value("  42  ", cleaners=StripCleaner(), convertor=IntConvertor()) == (True, 42)

    def test_cleaners_compose_left_to_right(self):
        result = process_value("  YES  ",
                               cleaners=[StripCleaner(), CapitalizationCleaner("lower")])
        assert result == (True, "yes")

    def test_a_failing_convertor_reports_invalid_without_raising(self):
        # ConvertorError is caught inside process_value and turned into (False, None)
        # rather than escaping to the caller.
        assert process_value("not a number", convertor=IntConvertor(),
                             error_callback=silent_error) == (False, None)

    def test_a_failing_validator_reports_invalid_and_discards_the_value(self):
        # Both failure modes look the same to the caller: (False, None). The
        # converted value is not handed back even though conversion succeeded.
        assert process_value("99", convertor=IntConvertor(),
                             validators=RangeValidator(1, 10),
                             error_callback=silent_error) == (False, None)

    def test_every_validator_must_pass(self):
        validators = [RangeValidator(1, 100), RangeValidator(50, 200)]
        assert process_value("75", convertor=IntConvertor(), validators=validators)[0] is True
        assert process_value("25", convertor=IntConvertor(), validators=validators,
                             error_callback=silent_error)[0] is False

    def test_no_convertor_leaves_the_value_a_string(self):
        assert process_value("42") == (True, "42")

    def test_the_error_callback_is_told_what_went_wrong(self):
        received = []

        def record(fmt_str, value, error_content):
            received.append((value, error_content))

        process_value("foo", convertor=IntConvertor(), error_callback=record)
        assert received == [("foo", "an integer number")]

    def test_a_custom_format_string_reaches_the_callback(self):
        received = []
        process_value("foo", convertor=IntConvertor(),
                      error_callback=lambda fmt, v, ec: received.append(fmt),
                      convertor_error_fmt="custom: {value}")
        assert received == ["custom: {value}"]


class TestChoiceConvertor:
    """Used internally by Table to map a typed tag to a row index; no direct test before."""

    def test_a_known_key_maps_to_its_value(self):
        assert convert(ChoiceConvertor({"a": 1, "b": 2}), "a") == 1

    def test_an_unknown_key_raises_convertor_error(self):
        with pytest.raises(ConvertorError):
            convert(ChoiceConvertor({"a": 1}), "z")

    def test_values_can_be_any_type(self):
        sentinel = object()
        assert convert(ChoiceConvertor({"key": sentinel}), "key") is sentinel

    def test_the_error_callback_is_called_before_raising(self):
        received = []
        with pytest.raises(ConvertorError):
            ChoiceConvertor({"a": 1})("z", lambda fmt, v, ec: received.append(v), "{value}")
        assert received == ["z"]


class TestListConvertor:
    def test_the_default_delimiter_is_a_comma(self):
        assert convert(ListConvertor(), "a,b,c") == ["a", "b", "c"]

    def test_an_empty_string_gives_an_empty_list(self):
        assert convert(ListConvertor(), "") == []

    def test_a_custom_delimiter_is_used(self):
        assert convert(ListConvertor(delimiter="|"), "a|b|c") == ["a", "b", "c"]

    def test_a_none_delimiter_sniffs_the_separator(self):
        assert convert(ListConvertor(delimiter=None), "a;b;c") == ["a", "b", "c"]

    def test_leading_space_after_the_delimiter_is_dropped(self):
        assert convert(ListConvertor(), "a, b,  c") == ["a", "b", "c"]


class TestIntConvertorBases:
    @pytest.mark.parametrize("base, text, expected", [
        (10, "42", 42),
        (16, "ff", 255),
        (2, "1011", 11),
        (8, "17", 15),
        (0, "0x1f", 31),
    ])
    def test_a_non_decimal_base_is_honoured(self, base, text, expected):
        assert convert(IntConvertor(base=base), text) == expected

    def test_a_value_illegal_in_the_given_base_raises(self):
        with pytest.raises(ConvertorError):
            convert(IntConvertor(base=2), "9")


class TestBooleanConvertorTokens:
    @pytest.mark.parametrize("text", ["t", "true", "y", "yes", "1", "TRUE", "Yes"])
    def test_truthy_tokens(self, text):
        assert convert(BooleanConvertor(), text) is True

    @pytest.mark.parametrize("text", ["f", "false", "n", "no", "0", "FALSE", "No"])
    def test_falsy_tokens(self, text):
        assert convert(BooleanConvertor(), text) is False

    def test_anything_else_raises(self):
        with pytest.raises(ConvertorError):
            convert(BooleanConvertor(), "maybe")


class TestDecimalConvertor:
    def test_a_plain_decimal_converts(self):
        assert convert(DecimalConvertor(), "3.14") == decimal.Decimal("3.14")

    def test_an_unknown_rounding_name_lists_the_legal_ones(self):
        # Regression guard for #48: this used to be a bare KeyError showing only the
        # bad name.
        with pytest.raises(ValueError, match="unknown rounding 'ROUND_SIDEWAYS'") as exc_info:
            DecimalConvertor(rounding="ROUND_SIDEWAYS")
        assert "ROUND_HALF_UP" in str(exc_info.value)

    @pytest.mark.parametrize("rounding, expected", [
        ("ROUND_DOWN", "1.99"),
        ("ROUND_UP", "2.00"),
        ("ROUND_HALF_UP", "2.00"),
        ("ROUND_HALF_DOWN", "2.00"),
        ("ROUND_FLOOR", "1.99"),
        ("ROUND_CEILING", "2.00"),
    ])
    def test_the_rounding_mode_is_applied(self, rounding, expected):
        # Regression guard for #48: every one of these returned 1.999 before the fix,
        # because Decimal(value, context) applies neither prec nor rounding.
        converted = convert(DecimalConvertor(precision=2, rounding=rounding), "1.999")
        assert converted == decimal.Decimal(expected)

    def test_the_rounding_modes_do_not_all_agree(self):
        # The reason this went unnoticed for so long: the original tests only used values
        # where ROUND_UP and ROUND_HALF_UP give the same answer, so an inert rounding mode
        # looked exactly like a working one.
        up = convert(DecimalConvertor(precision=2, rounding="ROUND_UP"), "1.234")
        down = convert(DecimalConvertor(precision=2, rounding="ROUND_DOWN"), "1.234")
        assert (up, down) == (decimal.Decimal("1.24"), decimal.Decimal("1.23"))

    def test_precision_counts_decimal_places_not_significant_digits(self):
        # The distinction that makes get_money(precision=2) mean whole cents: two digits
        # of 1234.567 is 1234.57, not 1.2E+3.
        assert convert(DecimalConvertor(precision=2), "1234.567") == decimal.Decimal("1234.57")
        assert convert(DecimalConvertor(precision=5), "123.456789") == decimal.Decimal("123.45679")

    def test_precision_pads_a_short_value_out_to_the_requested_places(self):
        assert str(convert(DecimalConvertor(precision=2), "10.1")) == "10.10"

    def test_zero_precision_rounds_to_a_whole_number(self):
        assert convert(DecimalConvertor(precision=0), "2.5") == decimal.Decimal("3")

    def test_a_negative_precision_rounds_left_of_the_decimal_point(self):
        assert convert(DecimalConvertor(precision=-2), "1234.5") == decimal.Decimal("1.2E+3")

    def test_no_precision_keeps_every_digit_entered(self):
        # The default rounds nothing, which is what it has always done in practice --
        # precision was inert before the fix.
        assert str(convert(DecimalConvertor(), "3.14159265358979")) == "3.14159265358979"
        assert convert(DecimalConvertor(), "-0.001") == decimal.Decimal("-0.001")

    def test_a_non_integer_precision_is_rejected_at_construction(self):
        with pytest.raises(ValueError, match="precision must be a whole number"):
            # A fractional precision is the point: the guard is for callers who are not
            # running a type checker.
            DecimalConvertor(precision=2.5)  # ty: ignore[invalid-argument-type]

    def test_junk_input_raises_convertor_error(self):
        # Regression guard for #48: decimal raises InvalidOperation, an ArithmeticError,
        # so the ValueError-only handler never fired and this escaped uncaught.
        with pytest.raises(ConvertorError):
            convert(DecimalConvertor(), "not a number")

    def test_junk_input_reaches_the_error_callback(self):
        reported = []
        with pytest.raises(ConvertorError):
            DecimalConvertor()("not a number", lambda fmt, value, content: reported.append(content),
                               "{value}")
        assert reported == ["a decimal number"]


class TestProcessValueWithTheseConvertors:
    def test_a_choice_convertor_feeding_a_validator(self):
        result = process_value("b", convertor=ChoiceConvertor({"a": 1, "b": 2}),
                               validators=RangeValidator(1, 2))
        assert result == (True, 2)

    def test_a_list_convertor_feeding_a_length_validator(self):
        assert process_value("a,b,c", convertor=ListConvertor(),
                             validators=LengthValidator(min_len=3))[0] is True
        assert process_value("a,b", convertor=ListConvertor(),
                             validators=LengthValidator(min_len=3),
                             error_callback=silent_error)[0] is False

    def test_a_choice_cleaner_and_validator_together(self):
        result = process_value("gr", cleaners=None, convertor=None,
                               validators=ChoiceValidator(["red", "green"]),
                               error_callback=silent_error)
        assert result[0] is False
