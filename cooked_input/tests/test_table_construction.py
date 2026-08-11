"""Tests for Table construction options not covered elsewhere.

Column names given as a whitespace-delimited string, case-sensitive tag matching,
the 'return' flavour of add_exit, the TABLE_ITEM_RETURN branch of run(), and which
RULE values TableStyle accepts for each axis.

Len Wanger, 2026
"""

import prettytable as pt
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


class TestAddExitValidation:
    def test_an_unrecognised_add_exit_value_is_rejected_at_construction(self):
        # The guard lives here, which is why refresh_items can assume the value is
        # one of the four legal ones and needs only to single out TABLE_ADD_RETURN.
        with pytest.raises(RuntimeError, match="unexpected value for add_exit"):
            make_table(col_names=["Value"], add_exit="return_row")


class TestTableWithNoRows:
    def test_an_exit_row_can_be_added_to_an_empty_table(self, capsys):
        # The exit row's width is taken from the first row, so an empty table has to
        # fall back to a single column rather than indexing into nothing.
        table = Table([], col_names=["Value"], add_exit=True)
        table.refresh_items(add_exit=True)

        assert table.get_num_rows() == 1
        assert table.get_row("exit").action == "exit"


class TestHiddenRows:
    def test_a_row_hidden_at_construction_is_not_rendered(self, capsys):
        # item_filter drops hidden rows before they are added, but a TableItem built
        # hidden reaches the table and has to be skipped when the rows are rendered.
        rows = [
            TableItem(["alpha"], tag="a"),
            TableItem(["beta"], tag="b", hidden=True),
            TableItem(["gamma"], tag="c"),
        ]
        table = Table(rows, col_names=["Value"])
        table.refresh_items()
        table.show_table()

        rendered = capsys.readouterr().out
        assert "alpha" in rendered and "gamma" in rendered
        assert "beta" not in rendered


class TestNonRefreshingTable:
    """refresh=False builds the rows once, at construction, and never again."""

    def test_the_rows_are_built_during_construction(self):
        rows = [TableItem(["alpha"], tag="a"), TableItem(["beta"], tag="b")]
        table = Table(rows, col_names=["Value"], add_exit=True, refresh=False)

        # A refreshing table has no rows until refresh_items runs; this one does.
        assert table.get_num_rows() == 3  # two rows plus the exit row
        assert table.get_row("exit").action == "exit"

    def test_show_table_does_not_rebuild_the_rows(self, capsys):
        rows = [TableItem(["alpha"], tag="a")]
        table = Table(rows, col_names=["Value"], refresh=False)

        # Mutating the source list has no effect: a non-refreshing table is a snapshot.
        rows.append(TableItem(["beta"], tag="b"))
        table.show_table()

        rendered = capsys.readouterr().out
        assert "alpha" in rendered
        assert "beta" not in rendered

    def test_the_menu_loop_runs_without_rebuilding_between_choices(self, fake_input, capsys,
                                                                   recording_action):
        calls, action = recording_action
        rows = [TableItem(["alpha"], tag="a", action=action),
                TableItem(["beta"], tag="b", action=action)]
        table = Table(rows, col_names=["Value"], add_exit=True, refresh=False)

        feeder = fake_input("a", "b", "exit")
        assert table.run() is True
        assert [tag for tag, _ in calls] == ["a", "b"]
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


class TestVerticalRules:
    """``TableStyle`` documents one set of RULE values for both axes, but prettytable
    has two enums and only three of the four constants appear in both."""

    @pytest.mark.parametrize("rule", [ci.RULE_FRAME, ci.RULE_ALL, ci.RULE_NONE])
    def test_a_rule_with_a_vertical_equivalent_is_kept(self, rule):
        style = TableStyle(vrules=rule)

        assert style.vrules == rule
        assert isinstance(style.vrules, pt.VRuleStyle)

    def test_a_prettytable_vrule_is_accepted_unchanged(self):
        # Nothing documents this spelling, but it is the type the attribute holds.
        style = TableStyle(vrules=pt.VRuleStyle.ALL)

        assert style.vrules is pt.VRuleStyle.ALL

    def test_rule_header_is_rejected_where_it_was_written(self):
        with pytest.raises(ValueError, match="RULE_HEADER"):
            TableStyle(vrules=ci.RULE_HEADER)

    def test_rule_header_is_still_legal_for_horizontal_rules(self):
        assert TableStyle(hrules=ci.RULE_HEADER).hrules is ci.RULE_HEADER

    def test_a_value_that_is_no_rule_at_all_is_rejected(self):
        # Annotations do not reach a caller who is not type checking, so the runtime
        # check earns its keep. ty is right about this call -- that is the test.
        with pytest.raises(ValueError, match="not a RULE value"):
            TableStyle(vrules=99)  # ty: ignore[invalid-argument-type]

    def test_assigning_after_construction_is_checked_too(self):
        style = TableStyle()

        with pytest.raises(ValueError, match="RULE_HEADER"):
            style.vrules = ci.RULE_HEADER

    def test_a_table_renders_with_every_legal_vrule(self, capsys):
        # The failure this guards against surfaced in refresh_items, not construction.
        for rule in (ci.RULE_FRAME, ci.RULE_ALL, ci.RULE_NONE):
            table = make_table(style=TableStyle(vrules=rule))
            table.refresh_items()
            table.show_table()

            assert "alpha" in capsys.readouterr().out
