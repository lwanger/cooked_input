
Change Log
==========

This is the change log for the cooked_input Python package,

github archive: https://github.com/lwanger/cooked_input

for the latest documentation, see: https://readthedocs.org/projects/cooked-input/

see TODO.md for list of TODO items

* unreleased:

  * added: type annotations on every function, method and class in the package, and a
    ``py.typed`` marker (PEP 561) so that downstream projects actually see them -- without
    that file in the installed package a consumer's type checker ignores the annotations
    entirely. ``cooked_input`` is now a typed library: ``get_int()`` is understood to return
    ``int | None``, and passing a ``str`` where an ``int`` belongs is reported at the call
    site rather than at run time. The annotations describe the existing API and change no
    behavior on their own; the fixes they turned up are listed separately below.

    Two of them are worth knowing about because they make the *documented* type honest
    rather than optimistic. The eight ``get_*`` convenience functions are annotated
    ``X | None``, not ``X``: with ``required=False`` a blank response has always returned
    **None**. And ``get_input``, ``process_value`` and ``Convertor.__call__`` are annotated
    ``Any``, because what they return is whatever the convertor produced.
  * added: ``ty`` and ``ruff`` run in CI as a ``types`` job. The two do different jobs:
    ``ty`` checks that the annotations are correct, and Ruff's ``ANN`` rules check that they
    exist at all, which ``ty`` has no way to report. ``ty`` is pinned exactly rather than
    floored -- it is pre-1.0 and its diagnostics move between releases. A ``docs`` job was
    added at the same time, mirroring the Python version and ``fail_on_warning`` of the Read
    the Docs build.
  * docs: parameter and return types are rendered from the annotations by
    ``sphinx-autodoc-typehints`` instead of being restated in the docstrings, and the 171
    ``:param <type> <name>:`` fields and 46 ``:rtype:`` fields have been reduced to one
    source of truth. A docstring type does not merely duplicate the signature -- it wins --
    so several had quietly gone stale: ``get_int`` was documented ``:rtype: int`` long after
    it learned to return **None** for a blank optional response, ``get_date`` likewise, and
    ``Table.get_action`` was documented ``:rtype: Callable`` when returning one of the
    ``TABLE_ITEM_*`` sentinel strings is normal. ``Table.get_row`` had taken its summary and
    its ``:return:`` from ``get_num_rows`` by copy-paste, and so claimed to return the number
    of rows in the table.
  * fixed: ``TableStyle(rows_per_page=None)`` -- documented as "no maximum" -- crashed on
    any attempt to move around the table. ``page_up``, ``page_down``, ``goto_end`` and
    ``refresh_items`` all did arithmetic on ``rows_per_page`` without checking it first, so
    each raised ``TypeError: unsupported operand type(s) for -: 'int' and 'NoneType'``;
    ``refresh_items`` did the same whenever an item filter shrank the table below the
    current start row. With no maximum the whole table is one page, so all four are now
    no-ops that leave every row on screen.
  * fixed: ``get_money`` was the one ``get_*`` function that could not accept a single
    cleaner. It built its cleaner list with ``list(cleaners)`` rather than
    ``put_in_a_list(cleaners)``, so ``get_money(cleaners=StripCleaner())`` raised
    ``TypeError: 'StripCleaner' object is not iterable`` while every sibling accepted it.
  * fixed: ``Table.do_action`` raised ``'str' object is not callable`` for a
    ``default_action`` that was neither one of the ``TABLE_RETURN_*`` names nor a function.
    It tested ``default_action is not None``, which it never is -- ``Table.__init__`` maps
    **None** to ``return_tag_action``. ``Table.run`` already tested the same value with
    ``callable()`` and reported it on stderr instead, so ``do_action`` now agrees with it and
    with its own contract of handing the row back when there is no action to run.
  * fixed: ``GetInput.process_value`` returned a bare ``(False, None)`` tuple on a
    conversion error rather than a ``ProcessValueResponse``. It unpacks the same, so the
    common ``valid, value = ...`` spelling was unaffected, but a caller reaching for
    ``.valid`` or ``.value`` -- which the docstring invites -- got ``AttributeError`` on
    exactly the failure path they were checking for.
  * fixed: ``string.Formatter.vformat`` was passed **None** where the sequence of positional
    format arguments belongs, at four places in ``get_table.py``. Header, footer and cell
    format strings reference ``action_dict`` by name only, so nothing ever indexed it, but a
    caller who wrote ``{0}`` got a ``TypeError`` rather than the ``IndexError`` that says
    what is actually wrong.
  * tests: package coverage reached 100% (branch coverage, source only) and the suite grew to
    456 tests. The CI floor is now ``--cov-fail-under=99`` -- deliberately one point below the
    measured value, so that a genuinely awkward line does not have to be answered with a
    ``# pragma: no cover``. Closing the last gaps removed two unreachable branches in
    ``get_table.py``: a second ``callable(item_filter)`` test that the guard above it had
    already made redundant, and a tag comparison in ``get_menu``'s ``default_choice`` loop that
    could never match, since menu items are built without tags and are matched by value or by
    position. No behavior changes.
  * changed: ``Cleaner``, ``Convertor`` and ``Validator`` are now real abstract base classes.
    They declared ``__metaclass__ = ABCMeta``, the Python 2 spelling, which is an inert class
    attribute on Python 3 -- so nothing was enforced: the bases instantiated and a subclass
    that forgot ``__call__`` returned **None** from every call instead of failing. For a
    validator that reads as "rejected", so the failure was silent as well as wrong.
    ``__call__`` is the only abstract method; ``__init__`` is deliberately not abstract, so a
    subclass that implements ``__call__`` alone still works. **A subclass that never
    implemented** ``__call__`` **now raises TypeError when instantiated.**
  * removed dead code in ``get_table.py``: an unreachable column-count ``RuntimeError``
    (every branch above it derived the column count from the field names, so the two could
    never disagree), a ``use_style`` in ``create_table`` whose two forwarded arguments were
    not among the options ``Table`` reads and so were silently ignored, an unread loop
    counter, and a commented-out ``refresh_buffer`` method. No behavior changes.
  * fixed: ``Table.scroll_up_one_row`` and ``Table.scroll_down_one_row`` had their bodies the
    wrong way round -- scrolling up moved the window toward *later* rows. Since
    ``Table._get_choice`` wires ``UpOneRowRequest`` straight through, a command bound to
    "scroll up one row" scrolled the view down. They now match their own docstrings and
    ``page_up``/``page_down``, which have always had up meaning earlier. **Anyone who wired
    up these commands will see them move the other way.**
  * fixed: ``get_menu`` returned a ``TableItem`` instead of ``'exit'`` when the user picked
    the automatically added Exit row. ``Table.do_action`` fell through and handed back the
    row, and a ``TableItem`` never equals ``'exit'``, so ``get_menu``'s own test for it was
    dead code and callers writing ``if get_menu(...) == 'exit':`` never took that branch.
    ``do_action`` now returns **None** for a row whose action is ``TABLE_ITEM_EXIT`` or
    ``TABLE_ITEM_RETURN`` -- choosing one of those is choosing no row, which is what
    ``Table.run`` has always assumed -- so ``Table.get_table_choice`` returns **None** there
    and ``get_menu`` returns ``'exit'`` as documented. **Callers of**
    ``Table.get_table_choice`` **that inspected the returned exit row will see None instead.**
  * fixed: a numeric ``default_choice`` never resolved in ``get_menu``, so the menu silently
    had no default and simply reprompted. The resolution loop ended with an unconditional
    ``break`` inside its ``try`` body, so only the first choice was ever examined; matching
    by text survived that only because ``int('green')`` raised ``ValueError`` before the
    ``break`` was reached. The numeric comparison was also off by one, testing 0-based
    positions against the 1-based tags the table assigns.
  * fixed: a table cell containing a brace-delimited word, such as ``{literal}`` in a
    template or a log line, raised ``KeyError`` and crashed on display. The fallback that
    doubles up braces only caught ``ValueError``, which is what an *unmatched* brace raises;
    a well-formed field reference naming something absent from ``action_dict`` raises
    ``KeyError`` instead.
  * fixed: ``DecimalConvertor`` ignored both ``precision`` and ``rounding``. It passed its
    ``decimal.Context`` to the ``Decimal`` constructor, where the context affects only error
    signalling -- neither setting was ever applied, so
    ``DecimalConvertor(precision=2, rounding='ROUND_DOWN')('1.999')`` returned ``1.999``.
    The value is now quantized to ``precision`` digits after the decimal point using the
    requested rounding rule, which is what the documentation has always described and what
    makes ``get_money(precision=2)`` return whole cents. **Numeric results change** for any
    caller who set ``precision`` and expected it to be honoured. ``precision`` now defaults
    to **None**, meaning "round nothing" -- the same thing the old inert default of 28 did in
    practice -- and a non-integer ``precision`` is rejected at construction.
  * fixed: ``DecimalConvertor`` let bad input escape as ``decimal.InvalidOperation``. That is
    an ``ArithmeticError``, so the ``except ValueError`` handler never fired: no
    ``ConvertorError`` was raised and ``error_callback`` was never called for this convertor.
  * fixed: ``DecimalConvertor`` raised a bare ``KeyError`` for an unknown ``rounding`` name.
    It now raises a ``ValueError`` naming the eight legal values.
  * fixed: four crashes and inconsistencies in the "nothing was supplied" case, where an
    empty list or ``None`` was passed where validators or cleaners were expected.
    ``in_any(value, [])`` and ``get_input(retries=0)`` both raised ``UnboundLocalError``
    from a variable that was only ever assigned inside a loop body that never ran --
    ``get_input(retries=0)`` now raises the ``MaxRetriesError`` the retry limit implies.
    ``not_in(value, None)`` rejected every value and reported "value cannot match
    <value>", naming a validator that did not exist, so ``NoneOfValidator(None)`` refused
    everything while ``AnyOfValidator(None)`` accepted everything; all three of
    ``in_all``, ``in_any`` and ``not_in`` now treat no validators as vacuously true.
    ``compose(value, [])`` returned ``None`` instead of the value, so composing no
    functions destroyed its input rather than acting as the identity. (``compose`` was
    not reachable this way through ``get_input``, which guards with ``if self.cleaners``,
    but it is a public function.)
  * fixed: ``get_input`` looped forever when a blank line was entered at a prompt with
    ``required=True`` and no ``default``. That case matched none of the branches in the
    retry loop, so ``retries`` was never incremented and ``max_retries`` was unreachable.
    A blank response is now treated like any other rejected value: it is reported through
    ``error_callback`` (as ``"" cannot be blank``) and counts against ``retries``, so the
    prompt is repeated and a finite ``retries`` eventually raises ``MaxRetriesError``.
    Note the behavior change for callers that relied on blank lines being skipped
    silently -- they now consume a retry and produce an error message.
  * fixed: ``Table.run()`` could never be exited with a blank entry. Line 933 read
    ``action - TABLE_ITEM_EXIT`` -- a ``-`` where ``=`` was meant -- so ``action`` was
    left unassigned on that path, raising ``UnboundLocalError`` on the first pass
    through the loop and ``TypeError`` on later ones.
  * fixed: ``Table.refresh_items()`` raised ``UnboundLocalError`` when given an
    ``item_filter`` that was truthy but not callable. It now raises a ``RuntimeError``
    naming what the argument should have been.
  * fixed: a stray ``print('Table:__init__: ')`` debug statement fired when ``Table``
    was constructed with an invalid ``add_exit`` value.
  * fixed: ``SimpleValidator`` discarded its ``name`` argument, so every failure
    message read "is not a valid None" no matter what name was given.
  * fixed: ``get_list`` raised ``AttributeError`` when given a non-string iterable as
    its ``default``. It used ``collections.Iterable``, which was removed from the
    ``collections`` namespace in Python 3.10 -- so this failed on every supported
    version.
  * added Python 3.14 support. The full test suite passes on 3.14 with the existing
    dependency versions, so no code or dependency changes were needed; 3.14 is now in
    the CI matrix, the tox envlist and the PyPI classifiers.
  * the minimum stays at Python 3.10. Nothing in cooked_input's own source requires it
    (the syntax floor is far older), but prettytable and dateparser both declare
    requires-python >= 3.10, and going lower would mean depending on older releases of
    both. Python 3.9 reached end of life in October 2025, so the older Pythons that
    would unlock are all unsupported anyway.

* v0.6.0:

  * updated dateparser to 1.4.2. The old 0.7.6 pin cannot run on modern Python: it
    raises "bad escape \\d" from the regex module while building its relative-date
    patterns, which broke DateConvertor entirely.
  * dropped Python 2 support: cooked_input now requires Python 3.10 or later.
  * removed the future dependency (raise_from replaced by native raise ... from ...).
  * switched from the abandoned veryprettytable to prettytable. RULE_* constants keep
    the same values, but are now prettytable HRuleStyle members.
  * fixed make_pretty_table, which raised AttributeError on every call.
  * removed the validus dependency; the get_user_info example now uses a local is_email.
  * fixed a Python 3.13 deprecation (re.sub count/flags passed positionally) and several
    invalid escape sequences that emitted SyntaxWarning.
  * packaging moved to a PEP 621 pyproject.toml. setup.py, setup.cfg, Pipfile, Pipfile.lock
    and requirements.txt have been removed. Installing is unchanged: pip install cooked_input.
  * the wheel is now tagged py3-none-any rather than py2.py3-none-any, matching the drop of
    Python 2 support.
  * removed the setuptools-git install requirement. It is a build-time setuptools plugin and
    was never needed at run time, so it is no longer pulled in when you install cooked_input.
  * dependency pins relaxed to lower bounds (prettytable >= 3.18.0, dateparser >= 1.4.2).
    cooked_input no longer forces exact versions on the applications that depend on it.
  * the license is declared as a PEP 639 SPDX expression instead of the deprecated
    "License :: OSI Approved" classifier.
  * copyright notices updated to 2017-2026.

  Project infrastructure (no effect on the installed package):

  * added a GitHub Actions test matrix covering Python 3.10 through 3.13 on Linux, plus
    Windows and macOS, and a job that builds the distributions and checks them with twine.
  * releases are published with PyPI trusted publishing (OIDC). No API token is stored in
    the repository.
  * added a dependabot configuration to keep the workflow actions current.

* v0.5.4:

  * added get_money
  * fixed import error on collections.Iterable (may be collections.abc.Iterable in old versions of Python).
  * fixed __repr__ method of RemoveCleaner (said it was ReplaceCleaner)

* v0.5.3:

  * hidden input was showing default value in prompt string. Replaced with ``"***"``

* v0.5.2:

  * added part two of the tutorial
  
* v0.5.1:

  * num_rows_per_page in style accepts None (no limit)

* v0.5.0:

  * added TableStyle to Tables and get_menu.

  * added create_table convenience function for creating tables.

  * return_row_action (TABLE_RETURN_ROW) changed to return the whole row including the tag.

  * fixed bug in ListConvertor to catch StopIteration exception caused by empty list

  * added tk_get_page example.

* v0.3.0:

  * added GetInput class

  * changed kwargs to options for all calls. Removed options from cleaners and validators

  * changed Cleaner, Convertor and Validator to abstract base classes (ABCMeta) and methods to abtract methods

  * added get_menu and Table classes (Table, TableItem, etc.)

  * added ConvertorError exception. Changed Convertors to use it

  * added ChoiceConvertor to support get_menu

  * ListConvertor now takes a GetInput instance to apply to each element in the list

  * ListValidator now passes the length of the list to the len_validator. Also accepts an error format string for the
        the length validation

  * fixed bug: menus now work if rows is a single MenuItem, not a list of MenuItems

  * modified get_menu example for new menu structure

  * added elem_validators to get_list to validate list items

  * added IsFileValidator

  * changed parameter names on Regex cleaner to match re.sub parameter names

  * added count parameter to RemoveCleaner

  * removed TableConvertor. This functionality has been replaced by the Table class.

  * added minimum and maximum parameters to get_date

  * added requirements to setup.py. Moved __version__ to version.py

* v0.2.12:

  * renamed ChoicesValidator to ChoiceValidator

  * added case_insentive flag to ChoicesCleaner

  * check AnyOf and NoneOf for list of values, not just list of validation functions. Allows
    saying: NoneOfValidator(['foo', 'bar'])

  * put cleaners, convertors and validators in alphabetic order in the documentation

* v0.2.11:

  * required option was backwards... fixed

  * added last_word style for CapitalizeCleaner


  * added isstring function to input_utils for detecting strings (and string-like things). This should
    handle strings (str, unicode, raw, bytes, etc.) more robustly, including sub-classes.

  * added print_function futures import so error_callback works in Python 2.x

  * more coverage tests

* v0.2.7:

  * Clean up of pypi setup, readme, and documentation.

  * Ran code through linters and found several issues.

* v0.2.3:

 * Added count option to ReplaceCleaner

 * Added RemoveCleaner

 * Added RegexCleaner

 * Added ChoiceCleaner

 * Added cleaner example, for choice, replace and regex cleaners.

 * Added default values to get_user_info example and pythonized the user table.

 * Added input_utils.py and put compose, make_pretty_table, and put_in_a_list in it.

 * Changed RegexValidator parameter from 'regex' to 'pattern' for consistency with RegexCleaner.

 * Fixed 2.7 incompatibilities. Passing all tests in Python 2.7 and 3.6 now. Added future to requirements.txt.
    Calling future.raisefrom in convertors.py broken.

* v0.2.2:

 * Added minimum and maximum parameters to get_int and get_float convenience functions.

* v0.2.1:

 * Added convenience functions for: get_sring, get_int, get_float, get_boolean, get_list, get_date, and get_yes_no.

 * Added examples of calling the convenience functions to the examples (e.g. get_ints, get_lists, get_strs, simple_input).

 * Updated the tutorial to use the get_int convenience function. Also show example of PasswordValidator.

 * Created exception for: MaxRetriesError (subclassed from RuntimeError), raised when the maximum number of retries is exceeded.

 * Created exception for: ValidationError (subclassed from ValueError), raised when a value does not pass validation.

 * Get_*, Convertors and validators now raise MaxRetriesExceeded and ValidationError.

 * Added pytest tests for getting ints and floats. A lot more case to add.

* v0.2.0:

 * Made a major change to how errors are handled. Added error_callbacks, convertor format strings, and
    validation convertor strings. This changed most of the code base and some of the examples.

 * Added print_error, log_error, and ignore_error error callback routines.


