"""Tests for Table.run(), the interactive menu loop.

This is the one place in the suite where a test could genuinely hang, so the
approach matters. Three things keep it safe, in order of importance:

1. The ``fake_input`` feeder raises ``EOFError`` when its script runs out, so the
   loop always terminates even when the exit path under test is broken.
2. Every test scripts its intended terminator explicitly, so a *correct* run never
   reaches ``EOFError`` -- reaching it means something is wrong.
3. Each test asserts ``feeder.remaining == 0``, proving the loop iterated exactly
   as many times as scripted. That catches a spurious extra iteration, which a
   timeout never would.

Len Wanger, 2026
"""

import pytest

from cooked_input import GetInputInterrupt, Table, TableItem


def make_table(rows, **kwargs):
    return Table(rows, col_names=["Value"], **kwargs)


@pytest.fixture
def menu_rows(recording_action):
    """Two selectable rows sharing one recording action."""
    calls, action = recording_action
    rows = [TableItem(["alpha"], tag="1", action=action), TableItem(["beta"], tag="2", action=action)]
    return calls, rows


class TestExitPaths:
    def test_blank_input_exits_the_menu(self, fake_input, menu_rows, capsys):
        # Regression test for `action - TABLE_ITEM_EXIT`, a '-' where '=' belonged.
        # Before that was fixed this raised UnboundLocalError on the first iteration
        # and TypeError on later ones, so blank input could never exit a menu.
        calls, rows = menu_rows
        feeder = fake_input("1", "")

        assert make_table(rows, required=False).run() is True
        # action_dict defaults to an empty dict, not None.
        assert calls == [("1", {})]
        assert feeder.remaining == 0

    def test_the_exit_row_exits_the_menu(self, fake_input, menu_rows, capsys):
        calls, rows = menu_rows
        feeder = fake_input("1", "2", "exit")

        assert make_table(rows, add_exit=True).run() is True
        assert [tag for tag, _ in calls] == ["1", "2"]
        assert feeder.remaining == 0

    def test_an_explicit_exit_action_on_a_row_exits(self, fake_input, capsys):
        rows = [TableItem(["quit now"], tag="q", action="exit")]
        feeder = fake_input("q")

        assert make_table(rows).run() is True
        assert feeder.remaining == 0


class TestActionDispatch:
    def test_each_choice_runs_its_own_action_in_order(self, fake_input, capsys):
        calls = []
        rows = [
            TableItem(["alpha"], tag="1", action=lambda row, ad: calls.append("first")),
            TableItem(["beta"], tag="2", action=lambda row, ad: calls.append("second")),
        ]
        feeder = fake_input("2", "1", "2", "")

        make_table(rows, required=False).run()
        assert calls == ["second", "first", "second"]
        assert feeder.remaining == 0

    def test_the_action_dict_is_handed_to_every_action(self, fake_input, menu_rows, capsys):
        calls, rows = menu_rows
        action_dict = {"shared": "state"}
        fake_input("1", "")

        make_table(rows, required=False, action_dict=action_dict).run()
        assert calls == [("1", action_dict)]

    def test_the_default_sentinel_falls_through_to_the_default_action(self, fake_input, capsys):
        seen = []
        rows = [TableItem(["alpha"], tag="1")]  # no action -> TABLE_ITEM_DEFAULT
        feeder = fake_input("1", "")

        make_table(rows, required=False, default_action=lambda row, ad: seen.append(row.tag)).run()
        assert seen == ["1"]
        assert feeder.remaining == 0

    def test_default_action_none_returns_the_tag(self, fake_input, capsys):
        # default_action=None is not "no action" -- Table maps it to
        # return_tag_action, so the default sentinel resolves to something callable.
        rows = [TableItem(["alpha"], tag="1")]
        table = make_table(rows, required=False, default_action=None)
        assert table.default_action.__name__ == "return_tag_action"

    def test_an_uncallable_default_action_is_reported_on_stderr(self, fake_input, capsys):
        # Reaching this branch takes a default_action that is neither one of the
        # recognised strings nor callable; Table stores such a value verbatim.
        rows = [TableItem(["alpha"], tag="1")]  # default sentinel
        fake_input("1", "")

        make_table(rows, required=False, default_action="not-callable").run()
        assert "default_action not set" in capsys.readouterr().err

    def test_an_unrecognised_action_is_reported_on_stderr(self, fake_input, capsys):
        rows = [TableItem(["alpha"], tag="1", action="not-an-action")]
        fake_input("1", "")

        make_table(rows, required=False).run()
        assert "no action specified" in capsys.readouterr().err


class TestInterrupts:
    def test_an_interrupt_from_an_action_keeps_the_menu_running(self, fake_input, capsys):
        calls = []

        def interrupting(row, action_dict):
            calls.append(row.tag)
            raise GetInputInterrupt("cancelled that one")

        rows = [TableItem(["alpha"], tag="1", action=interrupting)]
        feeder = fake_input("1", "1", "")

        # The menu survives the interrupt and keeps prompting.
        assert make_table(rows, required=False).run() is True
        assert calls == ["1", "1"]
        assert feeder.remaining == 0
        assert "cancelled that one" in capsys.readouterr().out

    def test_an_interrupt_from_the_default_action_ends_the_menu_with_false(self, fake_input, capsys):
        def interrupting(row, action_dict):
            raise GetInputInterrupt("stop everything")

        rows = [TableItem(["alpha"], tag="1")]  # default sentinel
        feeder = fake_input("1")

        # This is the one path that reports failure rather than True.
        assert make_table(rows, required=False, default_action=interrupting).run() is False
        assert feeder.remaining == 0


class TestRefreshItemsGuards:
    def test_a_non_callable_item_filter_is_rejected_with_a_clear_error(self):
        # Regression test: `filtered_items` was only assigned for None/True/callable,
        # so a truthy non-callable filter fell through to the loop with the name
        # unbound and raised UnboundLocalError instead of saying what was wrong.
        table = make_table([TableItem(["alpha"], tag="1")])
        with pytest.raises(RuntimeError, match="item_filter must be None, True, or a callable"):
            table.refresh_items(item_filter="not callable")

    def test_an_item_filter_returning_a_non_tuple_is_rejected(self):
        table = make_table([TableItem(["alpha"], tag="1")])
        with pytest.raises(RuntimeError, match=r"return a tuple \(hidden, enabled\)"):
            table.refresh_items(item_filter=lambda item, action_dict: True)

    def test_an_item_filter_can_hide_and_disable_rows(self):
        rows = [TableItem([name], tag=name) for name in ("keep", "hide", "disable")]
        table = make_table(rows)

        def only_keep(item, action_dict):
            hidden = item.tag == "hide"
            enabled = item.tag != "disable"
            return hidden, enabled

        table.refresh_items(item_filter=only_keep)
        # Hidden rows drop out of _rows entirely; disabled ones stay but are not
        # offered as choices.
        assert [row.tag for row in table._rows] == ["keep", "disable"]
        assert table.get_row("disable").enabled is False


class TestAddExitValidation:
    def test_an_unexpected_add_exit_value_raises(self):
        with pytest.raises(RuntimeError, match="unexpected value for add_exit"):
            make_table([TableItem(["alpha"], tag="1")], add_exit="maybe")

    def test_the_add_exit_error_does_not_print_debug_noise(self, capsys):
        # A stray print('Table:__init__: ') used to fire on the way to this raise.
        with pytest.raises(RuntimeError):
            make_table([TableItem(["alpha"], tag="1")], add_exit="maybe")
        assert capsys.readouterr().out == ""
