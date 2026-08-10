
Change Log
==========

This is the change log for the cooked_input Python package,

github archive: https://github.com/lwanger/cooked_input

for the latest documentation, see: https://readthedocs.org/projects/cooked-input/

see TODO.md for list of TODO items

* unreleased:

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


