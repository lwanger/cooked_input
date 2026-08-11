"""Tests for GetInputCommand and the table navigation commands.

Two layers here. The six ``*_cmd_action`` functions are unconditional raises, so
they are one-liners to test on their own. What matters is the layer above: that
``Table._get_choice`` catches each request and moves the pagination window, and
that ``GetInput.get_input`` handles the three COMMAND_ACTION_* responses.

Len Wanger, 2026
"""

import pytest

import cooked_input as ci
from cooked_input import (
    CommandResponse,
    GetInputCommand,
    GetInputInterrupt,
    Table,
    TableItem,
    TableStyle,
    get_input,
)


ROWS_PER_PAGE = 3
NUM_ROWS = 10


def make_table(commands=None, **kwargs):
    rows = [TableItem([f"row {i}"], tag=str(i)) for i in range(NUM_ROWS)]
    return Table(rows, col_names=["Value"], style=TableStyle(rows_per_page=ROWS_PER_PAGE),
                 commands=commands, **kwargs)


class TestCommandActionsRaise:
    """Each navigation action exists only to raise its request exception."""

    @pytest.mark.parametrize("action, request_exception", [
        (ci.first_page_cmd_action, ci.FirstPageRequest),
        (ci.last_page_cmd_action, ci.LastPageRequest),
        (ci.next_page_cmd_action, ci.PageDownRequest),
        (ci.prev_page_cmd_action, ci.PageUpRequest),
        (ci.scroll_up_one_row_cmd_action, ci.UpOneRowRequest),
        (ci.scroll_down_one_row_cmd_action, ci.DownOneRowRequest),
    ])
    def test_action_raises_its_request(self, action, request_exception):
        with pytest.raises(request_exception):
            action("/x", "", None)


class TestGetInputCommand:
    def test_the_command_forwards_its_dict_to_the_action(self):
        received = []

        def action(cmd_str, cmd_vars, cmd_dict):
            received.append((cmd_str, cmd_vars, cmd_dict))
            return CommandResponse(ci.COMMAND_ACTION_NOP, None)

        cmd_dict = {"context": "value"}
        command = GetInputCommand(action, cmd_dict)

        assert command("/help", "arg1 arg2") == CommandResponse(ci.COMMAND_ACTION_NOP, None)
        assert received == [("/help", "arg1 arg2", cmd_dict)]

    def test_repr_names_the_action_and_the_dict(self):
        command = GetInputCommand(ci.next_page_cmd_action, {"a": 1})
        assert "GetInputCommand(cmd_action=" in repr(command)
        assert "cmd_dict={'a': 1}" in repr(command)

    def test_command_response_is_an_action_value_pair(self):
        response = CommandResponse(ci.COMMAND_ACTION_USE_VALUE, 42)
        assert response.action == ci.COMMAND_ACTION_USE_VALUE
        assert response.value == 42


class TestCommandActionsInGetInput:
    """The three COMMAND_ACTION_* branches, plus the unknown-action guard."""

    def test_use_value_substitutes_the_commands_value(self, fake_input):
        commands = {"/answer": GetInputCommand(
            lambda cmd_str, cmd_vars, cmd_dict: CommandResponse(ci.COMMAND_ACTION_USE_VALUE, "42"))}

        feeder = fake_input("/answer")
        assert get_input(commands=commands) == "42"
        assert feeder.remaining == 0

    def test_nop_reprompts_without_returning(self, fake_input):
        calls = []

        def note(cmd_str, cmd_vars, cmd_dict):
            calls.append(cmd_str)
            return CommandResponse(ci.COMMAND_ACTION_NOP, None)

        feeder = fake_input("/note", "/note", "actual value")
        assert get_input(commands={"/note": GetInputCommand(note)}) == "actual value"
        # Two nops means the prompt was shown three times in all.
        assert calls == ["/note", "/note"]
        assert feeder.remaining == 0

    def test_cancel_raises_get_input_interrupt(self, fake_input):
        commands = {"/quit": GetInputCommand(
            lambda cmd_str, cmd_vars, cmd_dict: CommandResponse(ci.COMMAND_ACTION_CANCEL, None))}

        fake_input("/quit")
        with pytest.raises(GetInputInterrupt):
            get_input(commands=commands)

    def test_an_unknown_action_raises_runtime_error(self, fake_input):
        commands = {"/bad": GetInputCommand(
            lambda cmd_str, cmd_vars, cmd_dict: CommandResponse("not_a_real_action", None))}

        fake_input("/bad")
        with pytest.raises(RuntimeError, match="Unknown command action"):
            get_input(commands=commands)

    def test_the_command_receives_the_text_after_the_command_word(self, fake_input):
        received = []

        def action(cmd_str, cmd_vars, cmd_dict):
            received.append((cmd_str, cmd_vars))
            return CommandResponse(ci.COMMAND_ACTION_USE_VALUE, cmd_vars)

        fake_input("/echo  hello world")
        assert get_input(commands={"/echo": GetInputCommand(action)}) == "hello world"
        assert received == [("/echo", "hello world")]


ALL_NAV_COMMANDS = {
    "/n": GetInputCommand(ci.next_page_cmd_action),
    "/p": GetInputCommand(ci.prev_page_cmd_action),
    "/e": GetInputCommand(ci.last_page_cmd_action),
    "/h": GetInputCommand(ci.first_page_cmd_action),
    "/u": GetInputCommand(ci.scroll_up_one_row_cmd_action),
    "/d": GetInputCommand(ci.scroll_down_one_row_cmd_action),
}


class TestNavigationCommandsMoveTheTable:
    """Each request exception is caught by _get_choice and moves the window.

    Note that ``get_table_choice`` calls ``show_rows(0)`` itself before prompting,
    so a window set up beforehand is discarded. Every sequence below therefore
    starts from the first page and navigates with commands, which exercises the
    dispatch more thoroughly than pre-positioning would have.
    """

    def navigate(self, fake_input, *keystrokes):
        """Drive a table through some commands and a final row choice."""
        table = make_table(commands=ALL_NAV_COMMANDS)
        feeder = fake_input(*keystrokes)
        table.get_table_choice()
        assert feeder.remaining == 0
        return table.table.start, table.table.end

    def test_next_page_command_pages_down(self, fake_input, capsys):
        assert self.navigate(fake_input, "/n", "5") == (3, 6)

    def test_prev_page_command_pages_up(self, fake_input, capsys):
        assert self.navigate(fake_input, "/n", "/n", "/p", "5") == (3, 6)

    def test_last_page_command_jumps_to_the_end(self, fake_input, capsys):
        assert self.navigate(fake_input, "/e", "5") == (7, 10)

    def test_first_page_command_jumps_to_the_top(self, fake_input, capsys):
        assert self.navigate(fake_input, "/e", "/h", "5") == (0, 3)

    def test_paging_down_past_the_end_clamps(self, fake_input, capsys):
        assert self.navigate(fake_input, "/n", "/n", "/n", "/n", "/n", "5") == (7, 10)

    def test_paging_up_past_the_start_clamps(self, fake_input, capsys):
        assert self.navigate(fake_input, "/p", "/p", "5") == (0, 3)

    def test_scroll_down_command_moves_the_window_by_one_row(self, fake_input, capsys):
        assert self.navigate(fake_input, "/d", "5") == (1, 4)

    def test_scroll_up_command_moves_back_by_one_row(self, fake_input, capsys):
        # Regression guard for #46: '/u' used to move toward later rows, so this
        # sequence drifted forward instead of back.
        assert self.navigate(fake_input, "/d", "/d", "/u", "5") == (1, 4)

    def test_scroll_up_command_from_the_last_page_moves_back(self, fake_input, capsys):
        assert self.navigate(fake_input, "/e", "/u", "5") == (6, 9)

    def test_scrolling_up_past_the_start_clamps(self, fake_input, capsys):
        assert self.navigate(fake_input, "/u", "5") == (0, 3)

    def test_a_refresh_screen_interrupt_returns_to_the_first_page(self, fake_input, capsys):
        def refresh(cmd_str, cmd_vars, cmd_dict):
            raise ci.RefreshScreenInterrupt

        commands = dict(ALL_NAV_COMMANDS, **{"/r": GetInputCommand(refresh)})
        table = make_table(commands=commands)
        fake_input("/e", "/r", "5")
        table.get_table_choice()
        assert (table.table.start, table.table.end) == (0, 3)
