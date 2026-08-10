"""Tests for Table construction options not covered elsewhere.

Column names given as a whitespace-delimited string, case-sensitive tag matching,
the 'return' flavour of add_exit, and the TABLE_ITEM_RETURN branch of run().

Len Wanger, 2026
"""

import pytest

from cooked_input import (
    GetInputCommand,
    Table,
    TableItem,
    TableStyle,
    CommandResponse,
    COMMAND_ACTION_CANCEL,
)
import cooked_input as ci


def make_table(rows=None, **kwargs):
    rows = rows if rows is not None else [TableItem(["alpha"], tag="a"), TableItem(["beta"], tag="B")]
    return Table(rows, **kwargs)


TWO_COL_ROWS = [TableItem(["alpha", "here"], tag="a"), TableItem(["beta", "there"], tag="B")]


class TestColumnNamesAsAString:
    def test_a_whitespace_string_is_split_into_column_names(self, capsys):
        # col_names accepts either a list or a single space-delimited string.
        table = make_table(list(TWO_COL_ROWS), col_names="Name Location")
        table.refresh_items()
        table.show_table()

        rendered = capsys.readouterr().out
        assert "Name" in rendered and "Location" in rendered

    def test_a_list_of_column_names_works_the_same(self, capsys):
        table = make_table(list(TWO_COL_ROWS), col_names=["Name", "Location"])
        table.refresh_items()
        table.show_table()

        rendered = capsys.readouterr().out
        assert "Name" in rendered and "Location" in rendered


class TestCaseSensitivity:
    def test_tags_are_matched_case_insensitively_by_default(self, fake_input, capsys):
        table = make_table(col_names=["Value"], default_action="tag")
        fake_input("b")
        assert table.get_table_choice() == "B"

    def test_case_sensitive_requires_an_exact_tag(self, fake_input, capsys):
        table = make_table(col_names=["Value"], default_action="tag", case_sensitive=True)
        feeder = fake_input("b", "B")
        assert table.get_table_choice() == "B"
        # 'b' was rejected, so both scripted responses were consumed.
        assert feeder.remaining == 0


class TestAddExitFlavours:
    def test_add_exit_true_appends_an_exit_row(self):
        table = make_table(col_names=["Value"], add_exit=True)
        table.refresh_items(add_exit=True)
        assert table.get_row("exit").action == "exit"

    def test_add_exit_return_appends_a_return_row(self):
        # TABLE_ADD_RETURN labels the row 'return' but gives it the exit action --
        # the two are not distinguished in the menu loop.
        table = make_table(col_names=["Value"], add_exit=ci.TABLE_ADD_RETURN)
        table.refresh_items(add_exit=ci.TABLE_ADD_RETURN)

        assert table.get_row("return").action == "exit"

    def test_the_return_row_ends_the_menu(self, fake_input, capsys):
        table = make_table(col_names=["Value"], add_exit=ci.TABLE_ADD_RETURN)
        feeder = fake_input("return")

        assert table.run() is True
        assert feeder.remaining == 0

    def test_an_explicit_return_action_ends_the_menu(self, fake_input, capsys):
        # The TABLE_ITEM_RETURN branch of run() is only reachable by hand-setting
        # the action, since TABLE_ADD_RETURN produces TABLE_ITEM_EXIT instead.
        rows = [TableItem(["go back"], tag="r", action=ci.TABLE_ITEM_RETURN)]
        table = Table(rows, col_names=["Value"])
        feeder = fake_input("r")

        assert table.run() is True
        assert feeder.remaining == 0


class TestInterruptFromTheChoicePrompt:
    def test_an_interrupt_while_choosing_keeps_the_menu_running(self, fake_input, capsys):
        # A command that cancels raises GetInputInterrupt out of _get_choice. run()
        # catches it, reports it, and prompts again rather than exiting.
        cancel = GetInputCommand(
            lambda cmd_str, cmd_vars, cmd_dict: CommandResponse(COMMAND_ACTION_CANCEL, None))
        rows = [TableItem(["alpha"], tag="1", action="exit")]
        table = Table(rows, col_names=["Value"], commands={"/cancel": cancel})

        feeder = fake_input("/cancel", "1")
        assert table.run() is True
        assert feeder.remaining == 0


class TestRefreshRepagination:
    def test_the_window_is_clamped_when_the_table_shrinks(self):
        rows = [TableItem([f"row {i}"], tag=str(i)) for i in range(10)]
        table = Table(rows, col_names=["Value"], style=TableStyle(rows_per_page=3))
        table.refresh_items()
        table.show_rows(7)

        # Refreshing with fewer rows must pull the window back inside the table.
        table.refresh_items(rows=[TableItem(["only"], tag="only")])
        assert table.table.start == 0
