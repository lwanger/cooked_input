"""Type aliases shared across ``cooked_input`` modules.

Private on purpose: nothing here is re-exported from ``cooked_input/__init__.py``, so
this module claims no public API name and can be reshaped freely.

Every module in the package uses ``from __future__ import annotations``, so annotations
naming these aliases are never evaluated at runtime. That is what lets an alias here
mention a class from a module that in turn imports this one, without a circular import.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""

from __future__ import annotations

from typing import Any, Callable

#: What ``cooked_input`` calls to report a rejected value, invoked as
#: ``error_callback(fmt_str, value, error_content)``. ``fmt_str`` is a format string
#: taking ``{value}`` and ``{error_content}``; ``value`` is whatever the user typed, or
#: whatever it had been converted to by the time it was rejected, hence ``Any``.
#: :func:`~cooked_input.error_callbacks.print_error` is the default.
ErrorCallback = Callable[[str, Any, str], None]
