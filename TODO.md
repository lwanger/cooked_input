
# io_get_input TODO list

**TODO:**

* general:
    * Talk about main motivation
    * Talk about using for command line tools
    * Talk about using same cleaning, converting, and validation outside of CLI (e.g. apply to GUI.)
    * document value_error_strings in convertors
    * change name to cooked_input?
    * add convenience functions for common scenarios like: get_integer_input, get_float_input, etc. Automatically put in
        the correct convertor (IntConvertor).
    * show in documentation the motivation. first program is guess a number between 1 and 10. Show what you actually need
        to write to make it work safely. Then show with get_integer_input(min_val=1, max_val=10, prompt='type in a number')
    * decorators to make cleaners, convertors, etc.
    
* io_get_input:
    * list convertor (return as tuple or list? list of separators) and validator (check types at various positions, min and max length)
    * option to list choices in prompt_str (???)
    * show error for validation errors
    * autocomplete (???)
    * add color to prompts and error messages (use colorfy?)
    * add routine to make menus more easily

* io_get_table_input
    * make it easier to make tables from query results
    * allow showing multiple columns tables (with one column as value)
    * allow value column to show longer description, but type in value
    * allow typing unique first characters of a choice input?
       
* examples/tests:
    * add: date, database tables (sqlite), passwd change (login, passwd, new passwd w/ checking)
    * add: BooleanConvertor, ReplaceCleaner

* cleaners:
    * make default cleaners = [Stripcleaner]
    * cleaner for Unicode normalization
    * cleaner for html quoting/unquoting
    * make a single capitalization cleaner with parameter for upper, lower, or capitalized
    * strip sql injection when dealing with tables

* convertors:
    * add: list (return as list, validator elements?), boolean, file, path, email, etc.
    * add dollar convertor that has minimum of 0.00 and strips off $ sign and commas. Returns float
 
* validators:
    * add: date range, date day of week
    * get in_any validator
    * work with validus functions