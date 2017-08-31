
# cooked_input TODO list

**TODO:**

* general:
    * Improve the README file
    * Improve coverage of automated tests
    * Add queue_errors error handler. Use for an example to send flash_messages for Flask support. Add option to 
        validators to force running all validators vs. quiting after first error found.

* get_input:
    * send error messages to stderr?
    * option to list choices in prompt_str (???)? Show hints? Create Mini-language of /cmds
    * replace raw_input with version using sys.stdin.readline()
    * show all errors for validation errors? Perform like flash messages where can have a list of them?
    * provide kwarg to run all validators, instead of failing on first one, so can see all errors.
    * autocomplete (???)
    * add routine to make menus more easily

* get_table_input
    * make it easier to make tables from query results
    * allow showing multiple columns tables (with one column as value)
    * allow value column to show longer description, but type in value
    * allow typing unique first characters of a choice input?
    * add render_table method to allow printing other than prettytable

* tutorial:
    * Add tables (build-a-burger) to tutorial
    * add part 2 (and part 3?) to tutorial to show more examples: passwords (get_user_info), tables,
        menus, and databases?
    * move `more examples` to `how-to`?
           
* examples/tests:
    * add: date
    * example runner (install as an entry point script.) Use get_input for menus.

* cleaners:
    * add EncodingCleaner to encode the value (see str.encode)
    * cleaner for Unicode normalization and character encodings
    * cleaner for html quoting/unquoting
    * make a single capitalization cleaner with parameter for upper, lower, or capitalized
    * strip sql injection when dealing with tables

* convertors:
    * add: file, path, etc.
    * add dollar convertor that has minimum of 0.00 and strips off $ sign and commas. Returns float
 
* validators:
    * add: date range, date day of week
    * allow forcing to validate all validators instead of stopping on first failure
    * return list of all validation failures
    * provide list of hints for what is required
    * password validator should create hint of what's required for password