"""Tests for the module-level table helpers.

Covers create_rows and create_table, the four ``return_*_action`` row actions, the
show_table / get_table_input wrappers, and get_menu.

One thing that surprises people about ``create_rows``: the *first* field becomes the
row's tag and only the remaining fields become its values. So ``create_rows(items,
['name', 'location'])`` produces rows tagged by name with one value each.

Len Wanger, 2026
"""

import collections

import pytest

import cooked_input as ci
from cooked_input import (
    Table,
    TableItem,
    TableStyle,
    create_rows,
    create_table,
    get_menu,
    get_table_input,
    show_table,
)


Printer = collections.namedtuple("Printer", "name location model")


class HasAttributes:
    """An object create_rows must read with getattr."""

    def __init__(self, name, location, model):
        self.name = name
        self.location = location
        self.model = model


FIELDS = ["name", "location", "model"]
EXPECTED_TAG = "Beast"
EXPECTED_VALUES = ["IO-PROD", "Model One G2"]


class TestCreateRowsFetchStrategies:
    """create_rows picks one accessor from the first item and reuses it."""

    @pytest.mark.parametrize("item", [
        pytest.param(HasAttributes("Beast", "IO-PROD", "Model One G2"), id="getattr"),
        pytest.param({"name": "Beast", "location": "IO-PROD", "model": "Model One G2"}, id="dict"),
        pytest.param(["Beast", "IO-PROD", "Model One G2"], id="getitem"),
        pytest.param(Printer("Beast", "IO-PROD", "Model One G2"), id="namedtuple"),
    ])
    def test_every_supported_item_shape_produces_the_same_row(self, item):
        rows = create_rows([item], FIELDS)
        assert len(rows) == 1
        assert rows[0].tag == EXPECTED_TAG
        assert rows[0].values == EXPECTED_VALUES

    def test_gen_tags_numbers_the_rows_instead_of_using_the_first_field(self):
        items = [["Beast", "IO-PROD"], ["Ford2", "Dearborn"]]
        rows = create_rows(items, ["name", "location"], gen_tags=True)
        # With generated tags every field stays a value.
        assert [row.values for row in rows] == [["Beast", "IO-PROD"], ["Ford2", "Dearborn"]]

    def test_item_data_is_attached_to_every_row(self):
        shared = {"origin": "test"}
        rows = create_rows([["Beast", "IO-PROD"]], ["name", "location"], item_data=shared)
        assert rows[0].item_data == shared

    def test_add_item_to_item_data_keeps_the_original_object(self):
        printer = Printer("Beast", "IO-PROD", "Model One G2")
        rows = create_rows([printer], FIELDS, add_item_to_item_data=True)
        assert rows[0].item_data["item"] is printer

    def test_add_item_to_item_data_is_merged_into_supplied_item_data(self):
        # The two options compose: item_data is copied per row and 'item' added to
        # the copy, rather than one replacing the other.
        printer = Printer("Beast", "IO-PROD", "Model One G2")
        rows = create_rows([printer], FIELDS, item_data={"origin": "test"},
                           add_item_to_item_data=True)
        assert rows[0].item_data == {"origin": "test", "item": printer}


class TestCreateRowsErrors:
    def test_an_item_with_no_usable_accessor_raises(self):
        with pytest.raises(RuntimeError, match="needs one of getattr, get, or __getitem__"):
            create_rows([12345], ["name"])

    def test_an_item_shorter_than_the_field_list_raises(self):
        with pytest.raises(RuntimeError, match="cannot fetch field values"):
            create_rows([["only-one-value"]], ["name", "location"])


class TestRowActions:
    """The four built-in actions, each a single line."""

    @pytest.fixture
    def row(self):
        return TableItem(["first", "second"], tag="t1")

    def test_return_table_item_action_returns_the_row_itself(self, row):
        assert ci.return_table_item_action(row, {}) is row

    def test_return_row_action_returns_the_tag_then_the_values(self, row):
        assert ci.return_row_action(row, {}) == ["t1", "first", "second"]

    def test_return_tag_action_returns_just_the_tag(self, row):
        assert ci.return_tag_action(row, {}) == "t1"

    def test_return_first_col_action_returns_the_first_value(self, row):
        assert ci.return_first_col_action(row, {}) == "first"

    def test_return_first_col_action_raises_on_a_row_with_no_values(self):
        with pytest.raises(IndexError):
            ci.return_first_col_action(TableItem([], tag="empty"), {})


class TestCreateTable:
    def test_field_names_become_the_column_headings(self, fake_input, capsys):
        items = [["Beast", "IO-PROD"], ["Ford2", "Dearborn"]]
        table = create_table(items, ["name", "location"], ["Name", "Location"],
                             gen_tags=True, title="Printers")
        table.show_table()

        rendered = capsys.readouterr().out
        assert "Printers" in rendered
        for heading in ("Name", "Location"):
            assert heading in rendered

    def test_default_action_string_selects_a_builtin_action(self, fake_input, capsys):
        items = [["Beast", "IO-PROD"], ["Ford2", "Dearborn"]]
        table = create_table(items, ["name", "location"], ["Name", "Location"],
                             gen_tags=True, default_action="row")

        fake_input("2")
        assert table.get_table_choice() == [2, "Ford2", "Dearborn"]

    def test_the_field_names_default_to_the_field_list(self, capsys):
        # field_names is optional: without it the raw field names become the headings.
        items = [["Beast", "IO-PROD"], ["Ford2", "Dearborn"]]
        table = create_table(items, ["name", "location"], gen_tags=True)
        table.show_table()

        rendered = capsys.readouterr().out
        assert "name" in rendered and "location" in rendered

    def test_without_gen_tags_the_first_field_becomes_the_tag_column(self, capsys):
        # The first field is consumed as the tag, so it heads the tag column rather
        # than appearing as a value column of its own.
        items = [["Beast", "IO-PROD"], ["Ford2", "Dearborn"]]
        table = create_table(items, ["name", "location"])
        table.show_table()

        rendered = capsys.readouterr().out
        assert "name" in rendered and "location" in rendered
        # 'Beast' is the tag now, not a value.
        assert table.get_row("Beast").values == ["IO-PROD"]


class TestModuleLevelWrappers:
    def test_show_table_renders_the_table(self, capsys):
        rows = create_rows([["Beast", "IO-PROD"]], ["name", "location"], gen_tags=True)
        show_table(Table(rows, col_names=["Name", "Location"]))
        assert "Beast" in capsys.readouterr().out

    def test_get_table_input_delegates_to_get_table_choice(self, fake_input, capsys):
        rows = create_rows([["Beast", "IO-PROD"], ["Ford2", "Dearborn"]],
                           ["name", "location"], gen_tags=True)
        table = Table(rows, col_names=["Name", "Location"], default_action="tag")

        fake_input("1")
        assert get_table_input(table) == 1


class TestGetMenu:
    def test_a_choice_is_returned_by_its_generated_tag(self, fake_input, capsys):
        feeder = fake_input("2")
        assert get_menu(["red", "green", "blue"]) == 2
        assert feeder.remaining == 0

    def test_the_menu_shows_every_choice(self, fake_input, capsys):
        fake_input("1")
        get_menu(["red", "green", "blue"], title="Colors", prompt="Pick one")

        rendered = capsys.readouterr().out
        for choice in ("red", "green", "blue", "Colors"):
            assert choice in rendered

    def test_a_bad_choice_is_rejected_and_reprompted(self, fake_input, capsys):
        feeder = fake_input("nope", "3")
        assert get_menu(["red", "green", "blue"]) == 3
        assert feeder.remaining == 0

    def test_picking_exit_returns_the_exit_tag(self, fake_input, capsys):
        # Regression guard for #47: do_action handed back the TableItem for the exit row,
        # and a TableItem never equals a string, so get_menu's `result == 'exit'` test was
        # dead and callers doing `if get_menu(...) == 'exit':` never took that branch.
        fake_input("exit")
        result = get_menu(["red", "green"], add_exit=True)
        assert result == "exit"
        assert not isinstance(result, TableItem)

    def test_leaving_the_menu_blank_also_returns_the_exit_tag(self, fake_input, capsys):
        # The other way out of a menu, which has always worked, and now shares one branch
        # with picking Exit.
        fake_input("")
        assert get_menu(["red", "green"], add_exit=True, required=False) == "exit"

    def test_a_supplied_style_replaces_the_borderless_menu_default(self, fake_input, capsys):
        # A menu renders without borders unless the caller asks for a table style.
        fake_input("1")
        get_menu(["red", "green"], style=TableStyle(show_border=True, show_cols=True))
        assert "|" in capsys.readouterr().out

    def test_the_default_menu_style_has_no_borders(self, fake_input, capsys):
        fake_input("1")
        get_menu(["red", "green"])
        assert "|" not in capsys.readouterr().out

    def test_a_supplied_default_action_overrides_returning_the_tag(self, fake_input, capsys):
        # get_menu installs return_tag_action unless the caller named one.
        fake_input("2")
        assert get_menu(["red", "green"], default_action=ci.return_first_col_action) == "green"

    def test_a_default_choice_by_position_preselects_that_row(self, fake_input, capsys):
        # Menu items carry no tags, so a numeric default_choice matches the 1-based
        # position the table generates.
        feeder = fake_input("")
        assert get_menu(["red", "green", "blue"], default_choice="2") == 2
        assert feeder.remaining == 0

    def test_a_default_choice_by_value_preselects_that_row(self, fake_input, capsys):
        fake_input("")
        assert get_menu(["red", "green", "blue"], default_choice="green") == 2


class TestTableStyleOptions:
    def test_rows_per_page_reaches_the_table(self):
        rows = create_rows([[str(i)] for i in range(10)], ["value"], gen_tags=True)
        table = Table(rows, col_names=["Value"], style=TableStyle(rows_per_page=4))
        table.refresh_items()
        table.show_rows(0)
        assert (table.table.start, table.table.end) == (0, 4)

    def test_a_borderless_style_renders_without_pipes(self, capsys):
        rows = create_rows([["Beast"]], ["name"], gen_tags=True)
        table = Table(rows, col_names=["Name"], style=TableStyle(show_border=False))
        table.show_table()
        assert "|" not in capsys.readouterr().out
