"""Tests for the error callback contract and the library's exception types.

Every convertor and validator reports failure through a callback with the signature
``(fmt_str, value, error_content)``. The library hands over the template and the two
fields separately rather than a finished string, which is what lets ``silent_error``
discard the message without paying for the formatting.

Len Wanger, 2026
"""

import logging

import pytest

from cooked_input import (
    ConvertorError,
    DEFAULT_CONVERTOR_ERROR,
    DEFAULT_VALIDATOR_ERROR,
    IntConvertor,
    MaxRetriesError,
    RangeValidator,
    ValidationError,
    get_input,
    log_error,
    print_error,
    silent_error,
)


class TestPrintError:
    def test_the_message_goes_to_stderr_not_stdout(self, capsys):
        print_error(DEFAULT_CONVERTOR_ERROR, "foo", "an integer number")

        captured = capsys.readouterr()
        assert captured.out == ""
        assert '"foo" cannot be converted to an integer number' in captured.err

    def test_the_callback_does_the_formatting_itself(self, capsys):
        print_error("got {value}, wanted {error_content}", 3, "an even number")
        assert "got 3, wanted an even number" in capsys.readouterr().err


class TestSilentError:
    def test_nothing_is_written_anywhere(self, capsys):
        assert silent_error(DEFAULT_VALIDATOR_ERROR, "foo", "is wrong") is None

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""


class TestLogError:
    def test_the_message_is_logged_at_error_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            log_error(DEFAULT_VALIDATOR_ERROR, "foo", "is wrong")

        assert caplog.records[0].levelno == logging.ERROR
        assert '"foo" is wrong' in caplog.text


class TestDefaultFormatStrings:
    def test_the_convertor_default_names_the_value_and_the_target(self):
        message = DEFAULT_CONVERTOR_ERROR.format(value="foo", error_content="an integer number")
        assert message == '"foo" cannot be converted to an integer number'

    def test_the_validator_default_names_the_value_and_the_reason(self):
        message = DEFAULT_VALIDATOR_ERROR.format(value="foo", error_content="is too short")
        assert message == '"foo" is too short'


class TestExceptionTypes:
    @pytest.mark.parametrize("exception_type, base", [
        (MaxRetriesError, RuntimeError),
        (ValidationError, ValueError),
        (ConvertorError, ValueError),
    ])
    def test_each_exception_keeps_its_documented_base(self, exception_type, base):
        assert issubclass(exception_type, base)

    def test_the_message_survives_the_round_trip(self):
        assert str(ConvertorError("not a number")) == "not a number"


class TestCallbacksReachedThroughGetInput:
    def test_a_custom_callback_receives_the_convertors_error_content(self, fake_input):
        received = []

        def record(fmt_str, value, error_content):
            received.append((fmt_str, value, error_content))

        fake_input("foo", "42")
        assert get_input(convertor=IntConvertor(), error_callback=record) == 42
        assert received == [(DEFAULT_CONVERTOR_ERROR, "foo", "an integer number")]

    def test_a_custom_callback_receives_the_validators_error_content(self, fake_input):
        received = []

        def record(fmt_str, value, error_content):
            received.append((fmt_str, value, error_content))

        fake_input("99", "5")
        result = get_input(convertor=IntConvertor(), validators=RangeValidator(1, 10),
                           error_callback=record)
        assert result == 5
        assert len(received) == 1
        fmt_str, value, error_content = received[0]
        assert fmt_str == DEFAULT_VALIDATOR_ERROR
        assert value == 99
        # RangeValidator names the bound that was breached, not the whole range.
        assert error_content == "too high (max_val=10)"

    def test_silent_error_suppresses_output_entirely(self, fake_input, capsys):
        fake_input("foo", "42")
        assert get_input(convertor=IntConvertor(), error_callback=silent_error) == 42

        captured = capsys.readouterr()
        assert "cannot be converted" not in captured.err

    def test_the_caller_can_override_both_format_strings(self, fake_input, capsys):
        fake_input("foo", "42")
        get_input(convertor=IntConvertor(),
                  convertor_error_fmt="!! {value} is not {error_content} !!")

        assert "!! foo is not an integer number !!" in capsys.readouterr().err
