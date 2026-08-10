
# TODO

This is a list of changes I want to make to the project. These should be
made one at a time, not all at once. After each change, the code should be
reviewed by me, tests should be run to verify that the change does not break
anything, documentation should be updated, and the project should be committed
to git. Just before committing the code to git, move the TODO item to the "Completed" section. 

When the version number is incremented, move the items from the "Completed" section of this list into
a CHANGELOG.md file. The CHANGELOG.md file should be updated with the version number and date.


## First Things:

                                                                                                                                                                                               
  Done - Register the PyPI trusted publisher — owner lwanger, repo cooked_input, workflow release.yml, environment pypi. Exact match required. 
  1. Also create the pypi environment in repo settings;   
    adding yourself as required reviewer gives a manual gate before upload.                                                                                                                       
  2. Dry-run to TestPyPI via manual workflow_dispatch — release.yml has still never executed, so this is the first real test of the OIDC handshake, and it costs no version number.             
  3. Tag v0.6.0 to publish. The guard will refuse if the tag doesn't match __version__, which is currently 0.6.0.        

Two things I'd still flag before you cut 0.6.0:

- [ ] Push to github master
- [ ] Push to PYPI

**Second**:

- [ ] get_table.py sits at 66% coverage — 158 uncovered lines, mostly the interactive menu and pagination navigation. 
  That's the weakest spot in the package and it's the module the migration touched most.
- [ ] Add type hints
- [ ] Improve documentation and examples
- [ ] Improve test cases and coverage
- [ ] Update documentation to great-docs?

## Completed:

Items here move into CHANGELOG.md when the version number is incremented.

- [X] Update copyright statements to 2026. The nine copyright notices
      (`LICENSE`, `LICENSE.txt`, `docs/conf.py` and six module headers) now
      read `2017-2026`, keeping the first-publication year. The bare
      `Len Wanger, <year>` author lines in examples and tests were left
      alone: they record when a file was written, not a copyright claim.
- [X] Replace setup.py/Pipfile/requirements.txt with a pyproject.toml.
      Removed `setup.py`, `setup.cfg`, `Pipfile`, `Pipfile.lock` and
      `requirements.txt`; `tox.ini` now takes its dependencies from the
      `test` extra. Also finished the earlier `install_requires` pruning by
      dropping `setuptools-git`, a build-time plugin that was declared as a
      runtime dependency. Wheel tag narrows `py2.py3-none-any` ->
      `py3-none-any`, matching the drop of Python 2 support.

## more features:

- Split into sub-packages (input, menus, etc.)
- Simplify API? Emphasize convenience functions
- Add emoji support
- Work better with Unicode
- Add themes (**dict) so less verbose for calling with similar settings
- Bundles of inputs for forms? Relatonships/constraints between inputs?
- Make work better (extension?) to Pydantic?

## time-tracker plan:

- [X] Replace `veryprettytable` with `prettytable` (`get_table.py:17`, `input_utils.py:18,58`)
- [X] Prune `install_requires` (`setup.py:54`): drop `future` (Python 2 compat) and `setuptools-git`; confirm `validus`/`dateparser` are still needed
- [X] Declare and test a `>=3.12` floor (3.12 / 3.13 / 3.14)
- [ ] Push the 2 pending commits; release to PyPI (`0.5.5` or `0.6.0`)

**Others**:

* Focus on ease-of-use -- get_* functions.
* Restructure layers: ci_cleaners, ci_convertors, ci_validators, ci (get_*), ci_tables and ci_menus (TUI)
* Add model tooling (uv? lock files? Poetry?)
* add dash/zeal docset (add to: https://github.com/Kapeli/Dash-User-Contributions/tree/master/docsets) - https://kapeli.com/docsets#python
* add support for Rich (text color, tables, etc)
* full type hinting (run through mypy?)
* expand tutorials
* add support for rich consoles, rich tables?

* general:
    * Create extension directory (can add things with extra pip requirements like viridus)
    * Add profanity-check extension (https://github.com/vzhou842/profanity-check)
    * Add type hint stub files (*.pyi) 
    * _get_choice should create a GetInput instance and call get_input on it, instead of calling the GetInput.get_input
        convenience function (so don't have to reconstruct the GetInput everytime through the loop)
    * List processing - have process done on each list element - allows ChoiceCleaner on each element, etc.
    * Gray out visible but disabled entries in menus
    * Improve the README file
    * Add queue_errors error handler. Use for an example to send flash_messages for Flask support. Add option to 
        validators to force running all validators vs. quiting after first error found
    * get to 100% coverage and add badge
    * For consistency with wtform, should 'cleaners' be changed to 'filters'?
    * change put_in_a_list to tolist (consistent with memoryview)
    * Add bytearray type to isstring (doesn't match bytes, str, unicode or basestring)
    * Add get_password convenience function. Allow validating before and after calling a provided hashing function.
        (eg. check length, lower and uper case, etc. before hashing, then post-validation, such as comparing to 
        old password after)
    * Lock requirements to values suggested from PyUp.io 

* get_input:
    * get_input - bug in commands entering /filter, if /f is also a command, finds /f command
    * get_list is not right! not dealing with elem and list validators (should create a ListValidator)... comments wrong
    * add methods (or properties) for GetInput, TableItem and Table classes (e.g. set hrules in Table)
    * show all errors for validation errors? Perform like flash messages where can have a list of them?
    * provide kwarg/option to run all validators, instead of failing on first one, so can see all errors.
    * send error messages to stderr?

* get_string:
    * add minimum and maximum length parameters
    * add allowed/disallowed characters parameter. Nice to prevent SQL injection (i.e. no " or ;)
    
* get_menu:
    * add to tutorial - get_menu and Menu.run and setting parameters
    * add examples
    * add coverage tests
    * add ExitMenuExpception to exit a menu. Could be used from a menu action item to exit a menu

* get_table_input
    * get_row_num returns zero if table has not been inited... test or return # of table items.
    * refactor so all columns set in col_values and first element is tag (unless add_tag=True in which 
        case a number is inserted)
    * add:   header fmt str, footer fmt str, alignment, tag_alignment to TableStyle object
    * add footer w/ vformat with current row, page #, number of pages, etc. that can be put in the format string
    * Option to clip table values (maximum length and append '...')

* tutorial:
    * change to quick start?
    * Add tables (build-a-burger) to tutorial
    * add part 2 (and part 3?) to tutorial to show more examples: passwords (get_user_info), tables,
        menus, and databases?
    * more how-to examples (pick from examples)
    * move `more examples` to `how-to` in a separate file?
    * show how to get an object back - put in item data, return table item and get from item data.
           
* examples/tests:
    * clean up examples. With test coverage don't need to show so many cases.
    * add example for: DateConvertor and validators (e.g. RangeValidator)
    * example runner (install as an entry point script.) Use get_input for menus.
    * note to use sectets.compare.digest to compare passwords in get_password and other hidden values

* cleaners:
    * add swapcase and casefold styles to Capitalization
    * add EncodingCleaner to encode the value (see str.encode)
    * add cleaner to clean string from byte or bytearray to str (or unicode in 2.x)
    * Unicode support:
        * cleaner for Unicode normalization and character encodings
    * cleaner for html quoting/unquoting
    * cleaner for cross-site scripting (XSS)
    * strip sql injection when dealing with tables. See: https://pyup.io/posts/don-t-trust-user-input/ 
        Also see: https://github.com/JasonHinds13/hackable. https://xkcd.com/327/ Also: https://sqlparse.readthedocs.io/en/latest/
    * add: simple cleaner - take a callable in and clean. Like SimpleValidator. Useful for cleaning from
        large set of items. For example ChoiceCleaner on a large database table
    * make default cleaning do: strip, normalize Unicode, block sql injection, etc. Make a DefaultCleaner 
        class (subset of Cleaner) that can be used.

* convertors:
    * NameTuple convertor - pass in a NamedTuple type (from typing.NamedTuple if want default values)
      and a list of values. Returns an instance of the NamedTuple. l = [1,2,3]; def(cls, values):
      return cls(*l). Can check len of values list by len(_fields), or catch an exception (TypeError on __new__)
    * Dollar convertor that has minimum of 0.00 and strips off $ sign and commas. Returns float
    * Boolean convertor, add 'true_values' and 'false_values' lists
    * yes_no convertor, add 'yes_values' and 'no_values' lists
    * Time convertor, add so can get_time and compare times
    * Float convertor - add places, rounding and locale parameters/options
    * add a Complex convertor?
    * add: File convertor - pattern for name, suffix, path, check for existence, wildcard for multiple fields
    * add: simple convertor - take a callable in and convert. Like SimpleValidator. Useful for converting from
        large set of items. For example a database table
 
* validators:
    * validators to allow/disallow specific elements in a string or list. Nice for preventing quote or ;
         in a string to prevent SQL injection
    * add intersection_validator? See get_menu example. useful for filtering user roles.
    * add: date range, date day of week
    * allow forcing to validate all validators instead of stopping on first failure
    * return list of all validation failures
    * provide list of hints for what is required amongst all validators specified
    * password validator should create hint of what's required for password
    * have validators return True or False, with errors in self.errors? This is
    more consistent with wtform but feels less Pythonic. Have QueueErrors error_handler?
    * Add a URL validator, with require_tld
    * Add 'DataRequired' validator. This would check that the data coming into the validator
    is not None. Similar to wtform. Change 'required' option to 'input_required'?
    * Add 'OptionalValidator' w/ strip white space parm, sends StopValidation if not present? 
    Wtforms has this to allow a blank validation value.
    * For FloatValidators have a eta parameter for inexact comparisons (i.e. 2.0 +/- 0.000001)

* v0.3 and beyond:
    * Revamp tables and menus
        * allow typing unique first characters of a choice input?
        * add render_table method to allow printing other than prettytable
        * and lots more...
    * Can cleaners and convertor be merged to just a list of filters (i.e. a convertor is a 
    filter that changes the type)? Cleaners are always 
    on strings is easy, but could work on other types and chain. Are there filters you 
    want to do on other types (e.g. Scale a number?)
    * Can validators be combined with filters (i.e. a validator is just a filter that fails?)?
    * Need to look at scenarios. It is simpler but it requires keeping track of the type coming 
    out of each filter in the chain.
    * Alternatively, could have pre and post filters - pre-filters run on strings before
    conversion and validation; Post filters on the converted type (would this be before or
    after validation?)
    * option to list choices in prompt_str (???)? Show hints?
    * autocomplete, readline history and color. Required or can be done already(???)




