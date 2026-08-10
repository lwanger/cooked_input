"""Shared pytest fixtures for the cooked_input test suite.

cooked_input reads from the console, so nearly every test has to fake a keyboard.
This module provides the one supported way to do that: the ``fake_input`` fixture.

It replaces the older ``redirect_stdin`` context manager, which assigned ``sys.stdin``
directly. That approach could not reach the ``hidden=True`` code path safely --
:func:`getpass.getpass` ignores a reassigned ``sys.stdin`` whenever it can open
``/dev/tty``, so a test driving a hidden prompt reads the real keyboard on any
machine with a terminal attached.

Len Wanger, 2017-2026
"""

from __future__ import annotations

import builtins
import getpass
from collections import deque
from collections.abc import Callable, Iterable
from typing import Any

import pytest

from cooked_input import RULE_ALL, RULE_FRAME, Table, TableItem, TableStyle


def _as_lines(responses: Iterable[str]) -> list[str]:
    """Expand each response into one entry per line.

    ``str.splitlines()`` reproduces the old ``StringIO`` + ``input()`` semantics
    exactly, including the leading blank line and the whitespace-only final line
    that the triple-quoted inputs in this suite depend on. An empty string stays a
    single empty response -- the user pressing enter -- rather than vanishing.

    Args:
        responses: Strings the user "types". Each may contain embedded newlines.

    Returns:
        One response per line, in order.
    """
    lines: list[str] = []
    for response in responses:
        lines.extend(response.splitlines() or [""])
    return lines


class InputFeeder:
    """A scripted stand-in for the user typing at a terminal.

    Responses are handed out one per call, in order, to both :func:`builtins.input`
    (the visible path in ``GetInput.get_input``) and :func:`getpass.getpass` (the
    ``hidden=True`` path).

    When the script runs out the feeder raises ``EOFError``, which is exactly what a
    real ``input()`` does at end of stdin. That is the suite's primary hang guard: a
    retry loop or a ``Table.run()`` menu loop that would otherwise spin forever ends
    the test in microseconds with a readable failure instead of blocking the run.

    Attributes:
        prompts: Every prompt shown to the user, in order, visible and hidden alike.
        hidden_prompts: The subset of prompts that went through ``getpass``. A
            non-empty value proves a test actually exercised the hidden path.
    """

    def __init__(self, responses: Iterable[str]) -> None:
        self._pending: deque[str] = deque(responses)
        self.prompts: list[str] = []
        self.hidden_prompts: list[str] = []

    def __repr__(self) -> str:
        return f"InputFeeder(remaining={self.remaining}, prompts={len(self.prompts)})"

    @property
    def remaining(self) -> int:
        """How many scripted responses have not been consumed.

        Asserting this is ``0`` at the end of a test proves the code under test asked
        for exactly the inputs the test scripted -- the cheap way to catch a loop
        that iterated one time too many, which a timeout would never reveal.
        """
        return len(self._pending)

    def send(self, *responses: str) -> None:
        """Append more responses to the end of the script.

        Args:
            *responses: Strings the user types. Multi-line strings are split.
        """
        self._pending.extend(_as_lines(responses))

    def _take(self) -> str:
        if not self._pending:
            raise EOFError("InputFeeder script exhausted")
        return self._pending.popleft()

    def visible(self, prompt: str = "") -> str:
        """Stand in for :func:`builtins.input`.

        Args:
            prompt: The prompt cooked_input rendered.

        Returns:
            The next scripted response.

        Raises:
            EOFError: The script is exhausted.
        """
        self.prompts.append(prompt)
        return self._take()

    def hidden(self, prompt: str = "Password: ", stream: Any = None) -> str:
        """Stand in for :func:`getpass.getpass`.

        The signature matches getpass so a caller passing ``stream`` still works.

        Args:
            prompt: The prompt cooked_input rendered.
            stream: Ignored; accepted for signature compatibility with getpass.

        Returns:
            The next scripted response.

        Raises:
            EOFError: The script is exhausted.
        """
        self.prompts.append(prompt)
        self.hidden_prompts.append(prompt)
        return self._take()


@pytest.fixture
def fake_input(monkeypatch: pytest.MonkeyPatch) -> Callable[..., InputFeeder]:
    """Install a scripted stand-in for keyboard input.

    Call the fixture with the responses the user types; a multi-line string is split
    into one response per line. Calling it again inside the same test installs a
    fresh script, which is how the old ``redirect_stdin`` blocks behaved.

    ``builtins.input`` is patched rather than ``cooked_input.get_input.input``
    because ``GetInput.get_input`` calls the bare name, resolved against builtins at
    call time. Patching builtins therefore also covers the nested ``GetInput``
    instances driven from ``Table.run()`` and ``ListConvertor`` with no extra
    bookkeeping. ``monkeypatch`` undoes both patches at teardown, so the fixture
    nests and composes with ``capsys`` -- neither of which ``redirect_stdin`` did.

    Returns:
        A callable that installs the script and returns the :class:`InputFeeder`, so
        a test can inspect ``prompts``, ``hidden_prompts`` and ``remaining``.

    Example:
        >>> def test_retries_past_a_bad_value(fake_input):
        ...     feeder = fake_input("foo", "42")
        ...     assert get_int() == 42
        ...     assert feeder.remaining == 0
    """

    def install(*responses: str) -> InputFeeder:
        feeder = InputFeeder(_as_lines(responses))
        monkeypatch.setattr(builtins, "input", feeder.visible)
        monkeypatch.setattr(getpass, "getpass", feeder.hidden)
        return feeder

    return install


@pytest.fixture
def framed_style() -> TableStyle:
    """The bordered, all-rules table style the table tests share.

    Spelled out rather than relying on TableStyle's defaults, because these tests
    are partly about what the style arguments do.
    """
    return TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)


@pytest.fixture
def simple_table() -> Table:
    """A three-row, single-column table with an exit row, paginated two per page.

    Small enough to reason about and short enough to page through, so pagination
    tests do not each rebuild a table.
    """
    rows = [TableItem(["red"]), TableItem(["blue"]), TableItem(["green"])]
    return Table(rows, col_names=["Color"], add_exit=True, style=TableStyle(rows_per_page=2))


@pytest.fixture
def recording_action() -> tuple[list[tuple[Any, Any]], Callable[..., Any]]:
    """An action callable plus the list of ``(tag, action_dict)`` it was called with.

    Lets a menu-loop test assert on the *sequence* of actions taken rather than on
    printed output.

    Returns:
        A ``(calls, action)`` pair. ``calls`` is appended to on every invocation.
    """
    calls: list[tuple[Any, Any]] = []

    def action(row: Any, action_dict: Any) -> Any:
        calls.append((row.tag, action_dict))
        return row.tag

    return calls, action
