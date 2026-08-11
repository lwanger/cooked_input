"""Tests for Table's display surface and the remaining odds and ends.

Headers, footers, __repr__, __call__, the default_action string mapping, and the
refresh_items paths the other table test files do not reach.

Headers and footers are format strings resolved against the table's action_dict, so
a menu can show live state above and below the rows.

Len Wanger, 2026
"""

import pytest

from cooked_input import (
    Table,
    TableItem,
    TableStyle,
    create_rows,
    get_menu,
)


def make_table(rows=None, **kwargs):
    rows = rows if rows is not None else [TableItem(["alpha"], tag="1"), TableItem(["beta"], tag="2")]
    return Table(rows, col_names=["Value"], **kwargs)


class TestHeaderAndFooter:
    def test_a_header_is_printed_above_the_table(self, capsys):
        make_table(header="== Choose wisely ==").show_table()

        rendered = capsys.readouterr().out
        assert "== Choose wisely ==" in rendered
        assert rendered.index("== Choose wisely ==") < rendered.index("alpha")

    def test_a_footer_is_printed_below_the_table(self, capsys):
        make_table(footer="-- press enter to quit --").show_table()

        rendered = capsys.readouterr().out
        assert rendered.index("alpha") < rendered.index("-- press enter to quit --")

    def test_a_header_is_formatted_against_the_action_dict(self, capsys):
        table = make_table(header="Logged in as {user}", action_dict={"user": "len"})
        table.show_table()
        assert "Logged in as len" in capsys.readouterr().out

    def test_a_footer_is_formatted_against_the_action_dict(self, capsys):
        table = make_table(footer="{count} items", action_dict={"count": 2})
        table.show_table()
        assert "2 items" in capsys.readouterr().out

    def test_a_title_is_printed_when_given(self, capsys):
        make_table(title="Main Menu").show_table()
        assert "Main Menu" in capsys.readouterr().out

    def test_the_action_column_is_never_displayed(self, capsys):
        # Table appends an 'action' column internally and hides it at render time.
        make_table().show_table()
        assert "action" not in capsys.readouterr().out


class TestRepr:
    def test_repr_names_the_table_and_its_settings(self):
        table = make_table(title="Main Menu", prompt="Pick one")
        rendered = repr(table)

        assert rendered.startswith("Table(rows=")
        assert "title=Main Menu" in rendered
        assert "prompt=Pick one" in rendered


class TestCallableTable:
    def test_calling_a_table_runs_it_as_a_submenu(self, fake_input, capsys):
        # Table.__call__ ignores its arguments and calls run(), which is what lets a
        # Table be used directly as another table's action -- i.e. a submenu.
        calls = []
        rows = [TableItem(["alpha"], tag="1", action=lambda row, ad: calls.append(row.tag))]
        table = make_table(rows, required=False)

        feeder = fake_input("1", "")
        assert table(choice=None, action_dict=None) is True
        assert calls == ["1"]
        assert feeder.remaining == 0

    def test_a_table_can_be_used_as_another_tables_action(self, fake_input, capsys):
        inner_calls = []
        inner = make_table([TableItem(["deep"], tag="d",
                                      action=lambda row, ad: inner_calls.append("deep"))],
                           required=False)
        outer = make_table([TableItem(["submenu"], tag="s", action=inner)], required=False)

        feeder = fake_input("s", "d", "", "")
        outer.run()
        assert inner_calls == ["deep"]
        assert feeder.remaining == 0


class TestDefaultActionMapping:
    @pytest.mark.parametrize("name, expected_function", [
        ("tag", "return_tag_action"),
        ("first_value", "return_first_col_action"),
        ("row", "return_row_action"),
        ("table_item", "return_table_item_action"),
        (None, "return_tag_action"),
    ])
    def test_each_name_maps_to_its_builtin(self, name, expected_function):
        assert make_table(default_action=name).default_action.__name__ == expected_function

    def test_first_value_returns_the_first_column(self, fake_input, capsys):
        rows = create_rows([["Beast", "IO-PROD"]], ["name", "location"], gen_tags=True)
        table = Table(rows, col_names=["Name", "Location"], default_action="first_value")

        fake_input("1")
        assert table.get_table_choice() == "Beast"

    def test_a_callable_is_kept_as_given(self):
        def custom(row, action_dict):
            return "custom"

        assert make_table(default_action=custom).default_action is custom


class TestRefreshItems:
    def test_a_single_table_item_is_accepted_without_a_list(self):
        table = make_table()
        table.refresh_items(rows=TableItem(["solo"], tag="s"))

        assert table.get_num_rows() == 1
        assert table.get_row("s").values == ["solo"]

    def test_an_explicit_row_list_replaces_the_existing_rows(self):
        table = make_table()
        table.refresh_items(rows=[TableItem(["one"], tag="a"), TableItem(["two"], tag="b")])

        assert [row.tag for row in table._rows] == ["a", "b"]

    def test_add_exit_appends_an_exit_row(self):
        # Both the table option and the refresh_items argument have to agree: the
        # guard is `add_exit not in (False,'none') and self.add_exit not in
        # (False,'none')`, and self.add_exit defaults to 'none'. Passing add_exit
        # only to refresh_items is silently a no-op.
        table = make_table(add_exit=True)
        table.refresh_items(add_exit=True)

        assert table.get_row("exit").action == "exit"
        assert table.get_num_rows() == 3

    def test_add_exit_on_refresh_alone_does_nothing(self):
        table = make_table()  # constructed without the add_exit option
        table.refresh_items(add_exit=True)

        with pytest.raises(ValueError, match="not in the table"):
            table.get_row("exit")

    def test_an_unmatched_brace_in_a_cell_is_escaped(self):
        # Cell values go through vformat against the action_dict. A lone brace makes
        # vformat raise ValueError, and there is a doubling fallback for exactly that.
        table = Table([TableItem(["100% sure {"], tag="1")], col_names=["Value"])
        table.refresh_items()
        assert "{" in table.get_row("1").values[0]

    def test_a_brace_delimited_word_not_in_the_action_dict_is_shown_literally(self):
        # Regression guard for #47: the fallback only caught ValueError, but a cell like
        # "{literal}" parses as a valid field reference and raises KeyError instead, so
        # any table holding a {word} in its data crashed on display.
        table = Table([TableItem(["{literal}"], tag="1")], col_names=["Value"])
        table.refresh_items()
        assert table.get_row("1").values[0] == "{literal}"

    def test_a_log_line_full_of_braces_survives_display(self):
        table = Table([TableItem(['level={info} msg="{ok}"'], tag="1")], col_names=["Value"])
        table.refresh_items()
        assert table.get_row("1").values[0] == 'level={info} msg="{ok}"'

    def test_a_cell_placeholder_is_filled_from_the_action_dict(self):
        table = Table([TableItem(["hello {name}"], tag="1")], col_names=["Value"],
                      action_dict={"name": "world"})
        table.refresh_items()
        assert table.get_row("1").values[0] == "hello world"


class TestOptionalChoice:
    def test_a_blank_entry_returns_none_when_not_required(self, fake_input, capsys):
        table = make_table(required=False)
        feeder = fake_input("")

        assert table.get_table_choice() is None
        assert feeder.remaining == 0


class TestGetMenuDefaultChoice:
    def test_a_default_choice_is_shown_in_the_prompt(self, fake_input, capsys):
        feeder = fake_input("")
        get_menu(["red", "green", "blue"], default_choice="red")
        assert " (return for red)" in feeder.prompts[0]

    @pytest.mark.parametrize("choice, expected_tag", [("red", 1), ("green", 2), ("blue", 3)])
    def test_a_blank_entry_takes_a_default_named_by_value(self, fake_input, capsys,
                                                          choice, expected_tag):
        fake_input("")
        assert get_menu(["red", "green", "blue"], default_choice=choice) == expected_tag

    @pytest.mark.parametrize("choice, expected_tag", [("1", 1), ("2", 2), ("3", 3)])
    def test_a_blank_entry_takes_a_default_named_by_number(self, fake_input, capsys,
                                                           choice, expected_tag):
        # Regression guard for #47: the resolution loop ended with an unconditional
        # `break` inside its try body, so only the first choice was ever examined and a
        # numeric default never resolved -- the menu silently had no default and simply
        # reprompted. The comparison was also off by one against the 1-based tags.
        fake_input("")
        assert get_menu(["red", "green", "blue"], default_choice=choice) == expected_tag

    def test_an_integer_default_choice_works_as_well_as_a_string(self, fake_input, capsys):
        fake_input("")
        assert get_menu(["red", "green", "blue"], default_choice=2) == 2

    def test_a_default_choice_matching_nothing_leaves_the_menu_without_one(self, fake_input, capsys):
        # Out of range and not a value: nothing matches, so blank input just reprompts and
        # the feeder's exhaustion ends the test.
        fake_input("", "")
        with pytest.raises(EOFError):
            get_menu(["red", "green", "blue"], default_choice="9")


class TestTableStyleRendering:
    def test_hiding_the_column_headings(self, capsys):
        rows = create_rows([["Beast"]], ["name"], gen_tags=True)
        Table(rows, col_names=["Name"], style=TableStyle(show_cols=False)).show_table()

        rendered = capsys.readouterr().out
        assert "Beast" in rendered
        assert "Name" not in rendered
