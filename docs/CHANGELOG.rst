
Change Log
==========

This is the change log for the cooked_input Python package,

github archive: https://github.com/lwanger/cooked_input

for the latest documentation, see: https://readthedocs.org/projects/cooked-input/

see TODO.md for list of TODO items

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


