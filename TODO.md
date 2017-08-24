
# cooked_input TODO list

**TODO:**

* general:
    * Improve the README file
    * Add automated tests (pytest?)
    * Need to work on error messages. Not handled well now.
    * Add tables (build-a-burger) to tutorial
    * Review examples, tutorial interface. Clean up and make: easier, cleaner, more consistent.
        Are classes needed for Validators, Convertors, Cleaners, or can the be any callable? Convertors
        using error string only.
    * document value_error_strings in convertors
    * add convenience functions for common scenarios like: get_integer_input, get_float_input, etc. Automatically put in
        the correct convertor (IntConvertor).
    * decorators to make cleaners, convertors, etc. decorator for strip and lower cleaners? 
        get yes/no, get an int in a range, etc. Use decorators to reduce boilerplate code.
    * add part 2 (and part 3?) to tutorial to show more examples: passwords (get_user_info), tables,
        menus, and databases?

* get_input:
    * send error messages to stderr?
    * option to list choices in prompt_str (???)? Show hints?
    * replace raw_input with version using sys.stdin.readline()
    * show error for validation errors? Perform like flash messages where can have a list of them?
    * provide kwarg to run all validators, instead of failing on first one, so can see all errors.
    * autocomplete (???)
    * add routine to make menus more easily

* get_table_input
    * make it easier to make tables from query results
    * allow showing multiple columns tables (with one column as value)
    * allow value column to show longer description, but type in value
    * allow typing unique first characters of a choice input?
       
* examples/tests:
    * change to examples
    * add: date
    * add: ReplaceCleaner

* cleaners:
    * make default cleaners = [Stripcleaner]
    * cleaner for Unicode normalization
    * cleaner for html quoting/unquoting
    * make a single capitalization cleaner with parameter for upper, lower, or capitalized
    * make a single strip cleaner with parameter for left, right, or both
    * strip sql injection when dealing with tables

* convertors:
    * add: file, path, etc.
    * add dollar convertor that has minimum of 0.00 and strips off $ sign and commas. Returns float
 
* validators:
    * NotInValidator - if a value or list is passed in should use those as exact values. 
        NotInValidator('foo') causes a TypeError for now.
    * add: date range, date day of week
    * allow forcing to validate all validators instead of stopping on first failure
    * return list of all validation failures
    * provide list of hints for what is required
    * password validator should create hint of what's required for password