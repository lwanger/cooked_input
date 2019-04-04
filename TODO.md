
# cooked_input TODO list

**TODO:**

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
    * add minimum and maximum length paraeters
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




