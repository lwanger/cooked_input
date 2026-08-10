"""Tests for the standalone validator functions and the validators with no coverage.

test_validate.py already covers most validator classes through get_input. This file
takes the pieces it never reaches: the four module-level functions, IsFileValidator
(which had no test anywhere), and the branches that only show up when a validator is
called directly.

Len Wanger, 2026
"""

import pytest

from cooked_input import (
    DEFAULT_VALIDATOR_ERROR,
    AnyOfValidator,
    ChoiceValidator,
    EqualToValidator,
    IsFileValidator,
    LengthValidator,
    ListValidator,
    NoneOfValidator,
    RangeValidator,
    RegexValidator,
    SimpleValidator,
    print_error,
    silent_error,
)
from cooked_input.validators import in_all, in_any, not_in, validate


ONE_TO_TEN = RangeValidator(min_val=1, max_val=10)
TEN_TO_TWENTY = RangeValidator(min_val=10, max_val=20)


def quiet(value, validators):
    """Call a validator function with the noisy arguments filled in."""
    return validators(value, silent_error, DEFAULT_VALIDATOR_ERROR)


class TestInAll:
    def test_no_validators_passes(self):
        assert in_all(5, None, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_every_validator_must_pass(self):
        assert in_all(10, [ONE_TO_TEN, TEN_TO_TWENTY], silent_error, DEFAULT_VALIDATOR_ERROR) is True
        assert in_all(5, [ONE_TO_TEN, TEN_TO_TWENTY], silent_error, DEFAULT_VALIDATOR_ERROR) is False

    def test_a_single_callable_is_accepted_without_a_list(self):
        assert in_all(5, ONE_TO_TEN, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_a_bare_value_is_compared_for_equality(self):
        assert in_all(5, 5, silent_error, DEFAULT_VALIDATOR_ERROR) is True
        assert in_all(5, 6, silent_error, DEFAULT_VALIDATOR_ERROR) is False


class TestInAny:
    def test_no_validators_passes(self):
        assert in_any(5, None, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_one_passing_validator_is_enough(self):
        assert in_any(5, [ONE_TO_TEN, TEN_TO_TWENTY], silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_all_failing_validators_fail(self):
        assert in_any(50, [ONE_TO_TEN, TEN_TO_TWENTY], silent_error, DEFAULT_VALIDATOR_ERROR) is False

    def test_a_single_callable_is_accepted_without_a_list(self):
        assert in_any(5, ONE_TO_TEN, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_a_bare_value_is_compared_for_equality(self):
        assert in_any(5, 5, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_a_non_callable_inside_the_list_is_compared_for_equality(self):
        assert in_any(5, [ONE_TO_TEN, 99], silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_an_empty_validator_list_passes_vacuously(self):
        # Regression guard for #49: the loop body never runs, so `result` used to be
        # unbound here and in_any raised UnboundLocalError.
        assert in_any(5, [], silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_an_empty_validator_list_agrees_with_none_and_with_in_all(self):
        empty = in_any(5, [], silent_error, DEFAULT_VALIDATOR_ERROR)
        assert empty is in_any(5, None, silent_error, DEFAULT_VALIDATOR_ERROR)
        assert empty is in_all(5, [], silent_error, DEFAULT_VALIDATOR_ERROR)


class TestNotIn:
    def test_no_validators_passes_vacuously_and_says_nothing(self, capsys):
        # Regression guard for #49: the None branch used to set result = True, which is
        # read as "a validator matched", so this returned False and printed a
        # "value cannot match 5" message naming a validator that does not exist.
        assert not_in(5, None, print_error, DEFAULT_VALIDATOR_ERROR) is True
        assert capsys.readouterr().err == ""

    def test_no_validators_agrees_with_its_siblings(self):
        # The three used to disagree on the same input: in_all and in_any passed, not_in
        # rejected. All three now treat "nothing supplied" as vacuously true.
        assert not_in(5, None, silent_error, DEFAULT_VALIDATOR_ERROR) is True
        assert in_all(5, None, silent_error, DEFAULT_VALIDATOR_ERROR) is True
        assert in_any(5, None, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_an_empty_validator_list_passes_vacuously(self):
        assert not_in(5, [], silent_error, DEFAULT_VALIDATOR_ERROR) is True


class TestEmptyValidatorSetsThroughTheClasses:
    """The same #49 cases as reached by a caller, through the public validator classes."""

    def test_any_of_validator_with_an_empty_list_accepts(self):
        assert quiet(5, AnyOfValidator([])) is True

    def test_none_of_validator_with_no_validators_accepts(self):
        # This one rejected every value it was ever given before #49 was fixed.
        assert quiet(5, NoneOfValidator(None)) is True

    def test_none_of_validator_with_an_empty_list_accepts(self):
        assert quiet(5, NoneOfValidator([])) is True

    def test_none_of_validator_still_rejects_a_match(self):
        assert quiet(5, NoneOfValidator([ONE_TO_TEN])) is False

    def test_a_matching_validator_fails(self):
        assert not_in(5, [ONE_TO_TEN], silent_error, DEFAULT_VALIDATOR_ERROR) is False

    def test_no_matching_validator_passes(self):
        assert not_in(50, [ONE_TO_TEN], silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_a_single_callable_is_accepted_without_a_list(self):
        assert not_in(50, ONE_TO_TEN, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_a_bare_value_is_compared_for_equality(self):
        assert not_in(5, 5, silent_error, DEFAULT_VALIDATOR_ERROR) is False
        assert not_in(5, 6, silent_error, DEFAULT_VALIDATOR_ERROR) is True

    def test_the_failure_message_says_the_value_cannot_match(self, capsys):
        not_in(5, [ONE_TO_TEN], print_error, DEFAULT_VALIDATOR_ERROR)
        assert "cannot match" in capsys.readouterr().err


class TestValidate:
    def test_a_single_callable_is_accepted(self):
        assert validate(5, ONE_TO_TEN) is True

    def test_a_list_short_circuits_on_the_first_failure(self):
        calls = []

        def note(name, passes):
            def validator(value, error_callback, fmt_str):
                calls.append(name)
                return passes
            return validator

        assert validate(5, [note("first", False), note("second", True)]) is False
        assert calls == ["first"]

    def test_every_validator_passing_returns_true(self):
        assert validate(5, [ONE_TO_TEN, EqualToValidator(5)]) is True


class TestIsFileValidator:
    """This validator had no test anywhere in the suite before now."""

    def test_an_existing_file_passes(self, tmp_path):
        target = tmp_path / "real.txt"
        target.write_text("contents", encoding="utf-8")

        assert quiet(str(target), IsFileValidator()) is True

    def test_a_missing_path_fails(self, tmp_path):
        assert quiet(str(tmp_path / "absent.txt"), IsFileValidator()) is False

    def test_a_directory_is_not_a_file(self, tmp_path):
        assert quiet(str(tmp_path), IsFileValidator()) is False

    def test_the_failure_message_names_the_path(self, tmp_path, capsys):
        missing = str(tmp_path / "absent.txt")
        IsFileValidator()(missing, print_error, DEFAULT_VALIDATOR_ERROR)
        assert missing in capsys.readouterr().err

    def test_repr(self):
        assert repr(IsFileValidator()) == "IsFileValidator()"


class TestSimpleValidator:
    def test_a_truthy_result_passes(self):
        assert quiet(4, SimpleValidator(lambda value: value % 2 == 0)) is True

    def test_a_falsy_result_fails(self):
        assert quiet(3, SimpleValidator(lambda value: value % 2 == 0)) is False

    def test_the_name_reaches_the_error_message(self, capsys):
        # Regression test: __init__ used to set self._name = None, throwing the
        # caller's name away, so every message read "is not a valid None".
        validator = SimpleValidator(lambda value: False, name="even number")
        validator(3, print_error, DEFAULT_VALIDATOR_ERROR)

        message = capsys.readouterr().err
        assert "is not a valid even number" in message
        assert "None" not in message

    def test_the_default_name_is_used_when_none_is_given(self, capsys):
        SimpleValidator(lambda value: False)(3, print_error, DEFAULT_VALIDATOR_ERROR)
        assert "SimpleValidator value" in capsys.readouterr().err


class TestEqualToValidator:
    def test_a_matching_value_passes(self):
        assert quiet(5, EqualToValidator(5)) is True

    def test_a_differing_value_fails(self):
        assert quiet(6, EqualToValidator(5)) is False

    def test_a_none_target_accepts_anything(self):
        # EqualToValidator(None) is an always-pass mode rather than a test for None.
        validator = EqualToValidator(None)
        assert quiet(5, validator) is True
        assert quiet("anything", validator) is True


class TestRegexValidator:
    def test_a_matching_value_passes(self):
        assert quiet("5551234", RegexValidator(r"^\d{7}$")) is True

    def test_a_non_matching_value_fails(self):
        assert quiet("nope", RegexValidator(r"^\d{7}$")) is False

    def test_a_non_string_value_fails_rather_than_raising(self, capsys):
        assert RegexValidator(r"^\d+$")(12345, print_error, DEFAULT_VALIDATOR_ERROR) is False
        assert capsys.readouterr().err  # a message was produced

    def test_the_description_is_used_in_the_message_when_given(self, capsys):
        RegexValidator(r"^\d{7}$", regex_desc="a 7 digit number")(
            "nope", print_error, DEFAULT_VALIDATOR_ERROR)
        assert "a 7 digit number" in capsys.readouterr().err


class TestListValidator:
    def test_length_validators_constrain_the_list(self):
        validator = ListValidator(len_validators=RangeValidator(min_val=2, max_val=3))
        assert quiet([1, 2], validator) is True
        assert quiet([1], validator) is False
        assert quiet([1, 2, 3, 4], validator) is False

    def test_element_validators_constrain_each_item(self):
        validator = ListValidator(elem_validators=RangeValidator(min_val=0, max_val=9))
        assert quiet([1, 2, 3], validator) is True
        assert quiet([1, 99, 3], validator) is False

    def test_a_custom_length_message_is_used_when_supplied(self, capsys):
        validator = ListValidator(len_validators=RangeValidator(min_val=5),
                                  len_validator_fmt_str="wrong length: {value}")
        validator([1], print_error, DEFAULT_VALIDATOR_ERROR)
        assert "wrong length" in capsys.readouterr().err

    def test_no_validators_at_all_passes(self):
        assert quiet([1, 2, 3], ListValidator()) is True


class TestLengthAndChoiceEdges:
    def test_length_validator_rejects_a_value_with_no_length(self, capsys):
        assert LengthValidator(min_len=1)(12345, print_error, DEFAULT_VALIDATOR_ERROR) is False
        assert capsys.readouterr().err

    def test_length_validator_with_no_bounds_accepts_anything(self):
        assert quiet("any length at all", LengthValidator()) is True

    def test_choice_validator_lists_the_choices_in_its_message(self, capsys):
        ChoiceValidator(["red", "green"])("blue", print_error, DEFAULT_VALIDATOR_ERROR)
        message = capsys.readouterr().err
        assert "red" in message and "green" in message
