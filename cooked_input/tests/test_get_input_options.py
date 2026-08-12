"""Tests for GetInput's option handling and retry behaviour.

The per-type convenience wrappers are covered by test_get_int / test_get_str and
friends. This file takes the options they do not exercise: retries, defaults,
hidden prompts, and rejection of unknown options.

Len Wanger, 2026
"""

import decimal
import inspect
import logging
import sys
import typing

import pytest

import cooked_input as ci

from cooked_input import (
    Convertor,
    ConvertorError,
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


class _AsciiBytesConvertor(Convertor):
    """str -> bytes, standing in for the string-to-string-like conversion issue #83 raised.

    The library ships no such convertor; this is here to exercise the route get_string's
    docstring recommends. Reports and raises the way IntConvertor does.
    """

    def __init__(self, value_error_str="ascii text"):
        super().__init__(value_error_str)

    def __call__(self, value, error_callback, convertor_fmt_str):
        try:
            return value.encode("ascii")
        except UnicodeEncodeError as uee:
            error_callback(convertor_fmt_str, value, self.value_error_str)
            raise ConvertorError(str(uee)) from uee


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

    def test_zero_retries_raises_max_retries_error(self, fake_input):
        # Regression guard for #49: the loop body never runs, so this used to reach the
        # post-loop check with `valid_response` unbound and raise UnboundLocalError.
        feeder = fake_input("42")
        with pytest.raises(MaxRetriesError, match="Maximum retries exceeded"):
            get_input(retries=0)
        assert feeder.remaining == 1, "retries=0 should not have asked for input at all"


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
    """The ten options are named parameters, so an unrecognised one is rejected.

    These used to assert the opposite: that an unknown option was logged as a warning and
    construction carried on with the default. That let a misspelled option produce a prompt that
    looked almost right -- ``get_int(promt="Age?")`` asked "Enter a whole (integer) number".
    """

    def test_an_unknown_option_is_rejected(self):
        with pytest.raises(TypeError, match="bogus_option"):
            # ty is right that there is no such parameter -- that it can now say so is the
            # point of the change, and calling it anyway is the point of the test.
            GetInput(bogus_option=1)  # ty: ignore[unknown-argument]

    def test_an_unknown_option_is_rejected_by_the_convenience_functions(self):
        with pytest.raises(TypeError, match="bogus_option"):
            get_input(convertor=IntConvertor(), bogus_option=1)  # ty: ignore[unknown-argument]

    def test_a_misspelled_prompt_is_rejected_rather_than_ignored(self):
        with pytest.raises(TypeError, match="promt"):
            # no-matching-overload rather than unknown-argument, because get_int declares two
            # overloads on `required`: an unknown keyword makes every arm fail to match rather
            # than pointing at the one bad parameter. The runtime TypeError is unchanged.
            ci.get_int(promt="How old are you?")  # ty: ignore[no-matching-overload]


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
        feeder = fake_input("", "", "something")
        assert get_input(required=True, error_callback=silent_error) == "something"
        assert feeder.remaining == 0

    def test_blank_entries_count_against_the_retry_limit(self, fake_input):
        # The regression guard for #44: before the fix a blank response matched no
        # branch in the retry loop, so `retries` never moved and this spun forever.
        feeder = fake_input("", "", "")
        with pytest.raises(MaxRetriesError, match="Maximum retries exceeded"):
            get_input(required=True, retries=3, error_callback=silent_error)
        assert feeder.remaining == 0

    def test_a_blank_entry_is_reported_through_the_error_callback(self, fake_input):
        reported = []
        fake_input("", "something")
        get_input(
            required=True,
            error_callback=lambda fmt, value, content: reported.append(fmt.format(value=value, error_content=content)),
        )
        assert reported == ['"" cannot be blank']

    def test_a_blank_entry_mixes_with_other_rejected_values(self, fake_input):
        # A blank and a bad value should be counted the same way against `retries`.
        feeder = fake_input("", "nope")
        with pytest.raises(MaxRetriesError):
            get_input(convertor=IntConvertor(), required=True, retries=2, error_callback=silent_error)
        assert feeder.remaining == 0

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
        assert result is not None and result.year == 2020 and result.month == 6

    def test_a_date_before_the_minimum_is_rejected(self, fake_input):
        feeder = fake_input("1/1/2019", "6/15/2020")
        result = get_date(minimum=_as_date("1/1/2020"), error_callback=silent_error)
        assert result is not None and result.year == 2020
        assert feeder.remaining == 0

    def test_a_date_after_the_maximum_is_rejected(self, fake_input):
        fake_input("6/15/2021", "6/15/2020")
        result = get_date(maximum=_as_date("12/31/2020"), error_callback=silent_error)
        assert result is not None and result.year == 2020

    def test_a_caller_validator_is_combined_with_the_bounds(self, fake_input):
        # A single callable validator gets paired with the generated RangeValidator
        # rather than replacing it.
        not_june_first = SimpleValidator(lambda value: value.day != 1)
        fake_input("6/1/2020", "6/15/2020")
        result = get_date(minimum=_as_date("1/1/2020"), maximum=_as_date("12/31/2020"),
                          validators=not_june_first, error_callback=silent_error)
        assert result is not None and result.day == 15

    def test_no_bounds_leaves_the_validators_alone(self, fake_input):
        fake_input("6/15/2020")
        result = get_date()
        assert result is not None and result.year == 2020


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


class TestMoneyPrecisionAndRounding:
    """``precision`` and ``rounding`` are get_money's own parameters, not GetInput options.

    They used to arrive through the ``**options`` bag, which copied them into the convertor's
    arguments but never removed them from the bag -- so they were forwarded to GetInput as well,
    which did not know them and logged an "unknown option" warning for each. The documented way to
    ask for whole cents warned twice on every call.
    """

    def test_precision_rounds_to_whole_cents(self, fake_input):
        fake_input("$1234.567")
        assert get_money(precision=2) == decimal.Decimal("1234.57")

    def test_rounding_selects_the_rule(self, fake_input):
        fake_input("$1234.564")
        assert get_money(precision=2, rounding="ROUND_UP") == decimal.Decimal("1234.57")

    def test_no_precision_does_not_round(self, fake_input):
        fake_input("$1234.5678")
        assert get_money() == decimal.Decimal("1234.5678")

    def test_precision_no_longer_warns(self, fake_input, caplog):
        fake_input("$1234.567")
        with caplog.at_level(logging.WARNING):
            get_money(precision=2, rounding="ROUND_UP")

        assert caplog.text == ""


class TestValidatorsAsATuple:
    """A tuple of validators works everywhere a list does.

    ``get_int``, ``get_float`` and ``get_date`` built their validator list with
    ``validators + [range_validator]``, which needs a list on the left -- so a tuple raised
    TypeError as soon as a minimum or maximum was given too. ``get_string`` accepted one, because
    it extends a list instead, so the functions disagreed about what ``validators`` could be.
    """

    def test_get_int_takes_a_tuple_with_a_range(self, fake_input):
        fake_input("7")
        validators = (RangeValidator(min_val=1), RangeValidator(max_val=10))
        assert get_input(convertor=IntConvertor(), validators=validators) == 7

    def test_get_int_takes_a_tuple_alongside_minimum(self, fake_input):
        fake_input("7")
        assert ci.get_int(validators=(RangeValidator(min_val=1),), minimum=5) == 7

    def test_get_float_takes_a_tuple_alongside_minimum(self, fake_input):
        fake_input("7.5")
        assert ci.get_float(validators=(RangeValidator(min_val=1),), minimum=5) == 7.5

    def test_get_date_takes_a_tuple_alongside_minimum(self, fake_input):
        fake_input("2026-08-11")
        result = get_date(validators=(SimpleValidator(lambda v: True),),
                          minimum=DateConvertor()("2020-01-01", silent_error, ""))
        assert result is not None
        assert result.year == 2026

    def test_a_single_validator_still_works_alongside_minimum(self, fake_input):
        fake_input("7")
        assert ci.get_int(validators=RangeValidator(min_val=1), minimum=5) == 7


@pytest.mark.skipif(sys.version_info < (3, 11), reason="typing.get_overloads() needs 3.11")
class TestOverloadsMatchTheirImplementations:
    """The @overload pairs must keep the same parameters as the function they describe.

    Each get_* function states its signature three times: twice as overloads keyed on
    ``required``, once as the implementation. Nothing in Python keeps those in step, and a
    checker will not complain -- an option added to the implementation but missed on the
    overloads simply stops being callable for everyone using a type checker. That is the
    standing cost of writing them inline, so it is asserted rather than left to review.

    ``typing.get_overloads()`` arrived in 3.11 and ty checks against the 3.10 floor declared in
    pyproject.toml, so each use carries an ignore. The skipif above is what makes that safe: on
    3.10 the registry does not exist and none of this runs.
    """

    OVERLOADED = (get_string, ci.get_int, ci.get_float, ci.get_boolean,
                  get_date, ci.get_yes_no, get_money, get_list)

    @pytest.mark.parametrize("func", OVERLOADED, ids=lambda f: f.__name__)
    def test_both_overloads_take_the_implementation_s_parameters(self, func):
        overloads = typing.get_overloads(func)  # ty: ignore[unresolved-attribute]
        assert len(overloads) == 2, f"{func.__name__} should declare exactly two overloads"

        expected = list(inspect.signature(func).parameters)
        for overload_func in overloads:
            assert list(inspect.signature(overload_func).parameters) == expected

    @pytest.mark.parametrize("func", OVERLOADED, ids=lambda f: f.__name__)
    def test_the_two_overloads_are_keyed_on_required(self, func):
        # Strings, not typing objects: get_input.py uses `from __future__ import annotations`,
        # so nothing evaluates these at import time.
        annotations = [inspect.signature(f).parameters["required"].annotation
                       for f in typing.get_overloads(func)]  # ty: ignore[unresolved-attribute]
        assert annotations == ["Literal[True]", "Literal[False]"]

    @pytest.mark.parametrize("func", OVERLOADED, ids=lambda f: f.__name__)
    def test_only_the_required_true_arm_may_be_omitted(self, func):
        """The False arm must not default, or it claims `required` can be left out and still be False."""
        true_arm, false_arm = typing.get_overloads(func)  # ty: ignore[unresolved-attribute]
        assert inspect.signature(true_arm).parameters["required"].default is Ellipsis
        assert inspect.signature(false_arm).parameters["required"].default is inspect.Parameter.empty


class TestEveryGetterTakesTheSameOptions:
    """The get_* functions must accept one identical set of :class:`GetInput` options.

    docs/get_input_convenience.rst promises exactly this -- "Every function below accepts the
    same set of GetInput options" -- and callers lean on it to build an option dict once and
    splat it at whichever getter they need. A function quietly dropping one turns that into a
    TypeError at the call site, so the promise is asserted rather than left to review.

    ``get_string`` is the case that makes this worth pinning. It applies no convertor, so its
    ``convertor_error_fmt`` is accepted and ignored. Issue #83 settled that it stays: uniformity
    is the contract, and the rare case of converting a string to a string-like type (`bytes`,
    `bytearray`) belongs to ``get_input``, which does apply a convertor. The two tests at the end
    of this class pin both halves of that -- the option is harmless on ``get_string``, and the
    route it points at really works.
    """

    SHARED_OPTIONS = ("prompt", "required", "default", "default_str", "hidden", "retries",
                      "commands", "error_callback", "convertor_error_fmt", "validator_error_fmt")

    # The prompting functions documented as sharing the option set. process_value is excluded:
    # it takes a value instead of prompting, so prompt/required/retries do not apply to it.
    GETTERS = (get_string, ci.get_int, ci.get_float, ci.get_boolean, get_date,
               ci.get_yes_no, get_money, get_list, get_input)

    @pytest.mark.parametrize("func", GETTERS, ids=lambda f: f.__name__)
    def test_the_function_takes_every_shared_option(self, func):
        parameters = inspect.signature(func).parameters
        missing = [name for name in self.SHARED_OPTIONS if name not in parameters]
        assert not missing, f"{func.__name__} does not accept {missing}"

    @pytest.mark.parametrize("func", GETTERS, ids=lambda f: f.__name__)
    def test_the_shared_options_are_keyword_only(self, func):
        parameters = inspect.signature(func).parameters
        positional = [name for name in self.SHARED_OPTIONS
                      if parameters[name].kind is not inspect.Parameter.KEYWORD_ONLY]
        assert not positional, f"{func.__name__} takes {positional} positionally"

    # prompt is left out on purpose: each function supplies its own wording.
    @pytest.mark.parametrize("name", SHARED_OPTIONS[1:])
    def test_a_shared_option_defaults_the_same_way_everywhere(self, name):
        defaults = {func.__name__: inspect.signature(func).parameters[name].default
                    for func in self.GETTERS}
        first, *rest = defaults.values()
        assert all(default == first for default in rest), f"{name} defaults disagree: {defaults}"

    def test_get_string_accepts_the_ignored_convertor_error_fmt(self, fake_input):
        """Issue #83: passing it is a no-op, but it must not raise."""
        fake_input("hello")
        assert get_string(convertor_error_fmt="never used {value}") == "hello"

    def test_get_input_is_the_route_for_converting_a_string(self, fake_input, capsys):
        """The alternative get_string's docstring points at, kept honest.

        Converting to a string-like type goes through get_input, where a convertor really is
        applied -- so the value comes back converted and a failure reaches the caller's
        convertor_error_fmt, the two things get_string cannot do.
        """
        fake_input("café", "cafe")
        result = get_input(convertor=_AsciiBytesConvertor(),
                           convertor_error_fmt=">> {value} is not {error_content} <<")

        assert result == b"cafe"
        assert ">> café is not ascii text <<" in capsys.readouterr().err
