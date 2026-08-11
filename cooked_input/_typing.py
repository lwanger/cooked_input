"""Type aliases shared across ``cooked_input`` modules.

Private on purpose: nothing here is re-exported from ``cooked_input/__init__.py``, so
this module claims no public API name and can be reshaped freely.

``from __future__ import annotations`` makes *annotations* lazy, but an alias assignment is
ordinary code and evaluates its right-hand side at import time. So an alias naming a class
from a module that in turn imports this one -- :class:`~cooked_input.get_input.GetInput` and
:class:`~cooked_input.get_table.Table` both do -- has to leave that one name a string, or it
raises ``NameError`` against the ``TYPE_CHECKING`` import below.

Only the class name is quoted, never the whole alias. Everything around it is evaluated here,
where the names it uses are in scope. A wholly quoted alias is instead resolved later, in
whichever module *uses* it -- so it silently depends on that module happening to import
``Callable``, and ``sphinx_autodoc_typehints`` reports the ones that do not as unresolvable
forward references and falls back to printing the raw string.

:class:`~cooked_input.cleaners.Cleaner` needs no such treatment: ``cleaners`` imports nothing
from this module, so it can simply be imported.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Callable, TypeAlias

from .cleaners import Cleaner

if TYPE_CHECKING:
    from .get_input import CommandResponse
    from .get_table import TableItem

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
CleanerArg: TypeAlias = Cleaner | Iterable[Cleaner] | None

#: What a validator is called as: ``validator(value, error_callback, fmt_str)``. The return is
#: ``Any``, not ``bool``: a validator need only return something truthy, which is what lets
#: ``SimpleValidator(lambda s: re.match(...))`` work -- a ``Match`` object is truthy but is not a
#: **bool**. Collapsing that to a real boolean is the job of whoever calls the validator.
ValidatorFunc: TypeAlias = Callable[[Any, ErrorCallback, str], Any]

#: The ``validators`` argument :func:`~cooked_input.validators.validate` accepts: one validator, an
#: iterable of them, or **None** for nothing to check. Deliberately narrower than what the private
#: helpers in that module take, which also compare bare values for equality.
ValidatorArg: TypeAlias = ValidatorFunc | Iterable[ValidatorFunc] | None

#: What a :class:`~cooked_input.get_input.GetInputCommand` calls, invoked as
#: ``cmd_action(cmd_str, cmd_vars, cmd_dict)``.
CommandAction: TypeAlias = Callable[[str, str, dict[str, Any] | None], "CommandResponse"]

#: What a table row does when it is chosen, invoked as ``action(row, action_dict)``. The
#: return value becomes the result of
#: :meth:`~cooked_input.get_table.Table.get_table_choice`, so it is deliberately ``Any``.
#: A :class:`~cooked_input.get_table.Table` satisfies this too, which is how a table
#: becomes a sub-menu.
RowAction: TypeAlias = Callable[["TableItem", dict[str, Any]], Any]

#: Decides which rows a table shows, invoked as ``item_filter(row, action_dict)`` and
#: returning a ``(hidden, enabled)`` pair. Returning anything else is reported as a
#: ``RuntimeError`` by :meth:`~cooked_input.get_table.Table.refresh_items`.
ItemFilter: TypeAlias = Callable[["TableItem", dict[str, Any]], tuple[bool, bool]]
