"""Type aliases shared across ``cooked_input`` modules.

Private on purpose: nothing here is re-exported from ``cooked_input/__init__.py``, so
this module claims no public API name and can be reshaped freely.

Aliases naming a class from a module that in turn imports this one are written as strings
and marked ``TypeAlias``. ``from __future__ import annotations`` makes *annotations* lazy,
but an alias assignment is ordinary code and would evaluate its right-hand side at import
time -- so a plain assignment here would raise ``NameError`` against a ``TYPE_CHECKING``
import. The string form is what keeps the alias resolvable to a checker and inert at
runtime.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""

from __future__ import annotations

from collections.abc import Iterable  # noqa: F401  -- named by the string aliases below
from typing import TYPE_CHECKING, Any, Callable, TypeAlias

if TYPE_CHECKING:
    from .cleaners import Cleaner
    from .get_input import CommandResponse

#: What ``cooked_input`` calls to report a rejected value, invoked as
#: ``error_callback(fmt_str, value, error_content)``. ``fmt_str`` is a format string
#: taking ``{value}`` and ``{error_content}``; ``value`` is whatever the user typed, or
#: whatever it had been converted to by the time it was rejected, hence ``Any``.
#: :func:`~cooked_input.error_callbacks.print_error` is the default.
ErrorCallback: TypeAlias = Callable[[str, Any, str], None]

#: The ``cleaners`` argument accepted throughout the package: one cleaner, an iterable of
#: them applied in order, or **None** for no cleaning. Any callable taking the value and
#: returning it will do -- :func:`~cooked_input.input_utils.compose` only ever calls what
#: it is given.
CleanerArg: TypeAlias = "Cleaner | Iterable[Cleaner] | None"

#: What a :class:`~cooked_input.get_input.GetInputCommand` calls, invoked as
#: ``cmd_action(cmd_str, cmd_vars, cmd_dict)``.
CommandAction: TypeAlias = "Callable[[str, str, dict[str, Any] | None], CommandResponse]"
