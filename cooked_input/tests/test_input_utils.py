"""Tests for the input_utils helpers that test_utils.py does not reach.

test_utils.py covers compose, put_in_a_list, renumerate, swap_element and
cap_last_word. This file adds make_pretty_table and isstring, and the error
branches of compose.

Len Wanger, 2026
"""

import pytest

from cooked_input.input_utils import compose, isstring, make_pretty_table


class TestMakePrettyTable:
    def test_the_second_column_takes_the_given_name(self):
        table = make_pretty_table([(1, "beta"), (2, "alpha")], second_col_name="colour")
        rendered = table.get_string()

        assert "id" in rendered
        assert "colour" in rendered

    def test_rows_are_sorted_by_the_second_column_by_default(self):
        rendered = make_pretty_table([(1, "beta"), (2, "alpha")]).get_string()
        assert rendered.index("alpha") < rendered.index("beta")

    def test_sorting_can_be_switched_to_the_id_column(self):
        rendered = make_pretty_table([(1, "beta"), (2, "alpha")],
                                     sort_by_second_col=False).get_string()
        assert rendered.index("beta") < rendered.index("alpha")

    def test_every_row_appears(self):
        rows = [(i, f"item {i}") for i in range(5)]
        rendered = make_pretty_table(rows).get_string()
        for _, label in rows:
            assert label in rendered

    def test_an_empty_row_list_still_renders_the_header(self):
        rendered = make_pretty_table([]).get_string()
        assert "name" in rendered


class TestIsString:
    @pytest.mark.parametrize("value", ["text", "", b"bytes"])
    def test_strings_and_bytes_are_strings(self, value):
        assert isstring(value) is True

    @pytest.mark.parametrize("value", [5, 5.0, None, ["a"], {"a": 1}, ("a",)])
    def test_everything_else_is_not(self, value):
        assert isstring(value) is False


class TestCompose:
    def test_a_single_callable_is_applied(self):
        assert compose("  x  ", str.strip) == "x"

    def test_functions_are_applied_left_to_right(self):
        assert compose("  Hello  ", [str.strip, str.lower]) == "hello"

    def test_an_empty_function_list_is_the_identity(self):
        # Regression guard for #49: `result` was initialised to None and the loop never
        # runs, so composing nothing used to destroy the value instead of passing it on.
        assert compose("unchanged", []) == "unchanged"

    def test_a_non_callable_non_iterable_raises(self):
        with pytest.raises(RuntimeError, match="funcs cannot be called"):
            compose("value", 42)
