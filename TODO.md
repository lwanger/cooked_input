
# cooked_input TODO list

**TODO:**

* general:
    * Add tables (build-a-burger) to tutorial
    * Review examples, tutorial interface. Clean up and make: easier, cleaner, more consistent.
        Are classes needed for Validators, Convertors, Cleaners, or can the be any callable? Convertors
        using error string only.
    * Talk about using same cleaning, converting, and validation outside of CLI (e.g. apply to GUI.)
    * document value_error_strings in convertors
    * add convenience functions for common scenarios like: get_integer_input, get_float_input, etc. Automatically put in
        the correct convertor (IntConvertor).
    * decorators to make cleaners, convertors, etc. decorator for strip and lower cleaners? 
        get yes/no, get an int in a range, etc.
    * show how to use with a web form or tkinter form
    
* get_input:
    * send error messages to stderr?
    * option to list choices in prompt_str (???)
    * show error for validation errors
    * autocomplete (???)
    * add color to prompts and error messages (use colorfy?)
    * add routine to make menus more easily

* get_table_input
    * make it easier to make tables from query results
    * allow showing multiple columns tables (with one column as value)
    * allow value column to show longer description, but type in value
    * allow typing unique first characters of a choice input?
       
* examples/tests:
    * change to examples
    * add: date, 
    * add: ReplaceCleaner

* cleaners:
    * make default cleaners = [Stripcleaner]
    * cleaner for Unicode normalization
    * cleaner for html quoting/unquoting
    * make a single capitalization cleaner with parameter for upper, lower, or capitalized
    * strip sql injection when dealing with tables

* convertors:
    * add: file, path, etc.
    * add dollar convertor that has minimum of 0.00 and strips off $ sign and commas. Returns float
 
* validators:
    * add: date range, date day of week
    * get in_any validator
