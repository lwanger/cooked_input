.. currentmodule:: cooked_input

Cooked Input Quick Start
************************

Getting started in `cooked_input` is very easy. This quick start shows how to use `cooked_input` to get simple
keyboard input from the user. For more advanced appplications see the `tutorial <tutorial.html>`_ and `how to
<how_to.html>`_ sections.


Installing cooked_input:
========================

To install `cooked_input`::

    pip install cooked_input

Getting Simple Values:
======================

All `cooked_input` applications start with importing the `cooked_input` library::

    import cooked_input as ci

Getting Strings:
----------------

The simplest usage of `cooked_input` is to use
`get_string <file:///C:/Users/len_w/OneDrive/Documents/IO/code/cooked_input/build/sphinx/html/get_input_convenience.html#get-string>`_
to get a string value::

    ci.get_string(prompt="What is your name?")

Running this code produces::

    >>> ci.get_string(prompt="What is your name?")

    What is your name?: john cleese
    'john cleese'

This acts just like the Python `input <https://docs.python.org/3/library/functions.html?highlight=input#input>`_
command (or `raw_input` in legacy Python.) Unlike `input` `cooked_input` will
keep on asking until you enter valid input. `Get_string` will not accept a blank line.

.. note::

    To allow `get_string` to accept a blank line, like `input <https://docs.python.org/3/library/functions.html?highlight=input#input>`_,
    set the ``required`` parameter to **False**::

        ci.get_string(prompt="What is your name?", required=False)

Since we are entering a name, we want to make sure the value is capitalized. `Cooked_input` provides a number of `cleaners <cleaners.html>`_
that can be used to clean up the input value. :class:`CapitalizationCleaner` can be used to change the case of the
value. It takes a ``style`` parameter to say how you want the value changed. In this case we want use use ``ALL_WORDS_CAP_STYLE``
to capitalize the first letter of each of the words in the value::

    cap_cleaner = ci.CapitalizationCleaner(style=ci.ALL_WORDS_CAP_STYLE)
    ci.get_string(prompt="What is your name?", cleaners=[cap_cleaner])

Now the input will be cleaned up with the proper capitalization::

    >>> ci.get_string(prompt="What is your name?", cleaners=[cap_cleaner])

    What is your name?: jOhn CLeEse
    'John Cleese'

This is just one of the capitalization options. For the full list see the documentation for :class:`CapitalizationCleaner`.

Getting Integers:
-----------------

`Cooked_input` has a number of `convenience functions <get_input_convenience.html>`_ to get different input types.
Integers can be fetched using the
`get_int <file:///C:/Users/len_w/OneDrive/Documents/IO/code/cooked_input/build/sphinx/html/get_input_convenience.html#get-int>`_ function::

    ci.get_int(prompt="How old are you?", minimum=1)

`get_int` requests the input and returns a whole number (i.e. an integer.) If the input cannot be converted to an integer
it will print an error message and ask the user again. `Get_int` can also take parameters for the ``minimum``
and ``maximum`` values allowed. Since we are asking for a person's age, we want to make sure the number is a positive
number (i.e. the person is at least 1 year old.) Since no ``maximum`` value is given in this example there is no
maximum age for this input::

    >>>  ci.get_int(prompt="How old are you?", minimum=1)

    How old are you?: abc
    "abc" cannot be converted to an integer number
    How old are you?: 0
    "0" too low (min_val=1)
    How old are you?: 67
    67

This is just the tip of the iceberg of what `get_int` can do. There are a lot of examples of using `get_int` in
`get_ints.py` in the `cooked_input` examples directory. `Get_ints.py` shows examples of more complicated restrictions
on the allowed number (validators), suggesting default values, and other more advanced usages of `get_int`.
The `examples` directory is a good place to look to see how to use many of `cooked_input`'s features.

Getting Dates:
--------------

A good example of how `cooked_input` can be helpful is
`get_date <file:///C:/Users/len_w/OneDrive/Documents/IO/code/cooked_input/build/sphinx/html/get_input_convenience.html#get-date>`_.
`Get_date` is used to get dates and times (more specifically a Python
`datetime <https://docs.python.org/3/library/datetime.html#time-objects>`_ value.) The following code shows how to
ask the user for their birthday. Today's date is used in the example
below as the ``maximum`` beause it doesn't make sense that the user's birthday is in the future::

    import datetime
    today = datetime.datetime.today()
    birthday = ci.get_date(prompt="What is your birthday?", maximum=today)
    print(birthday)

Running this returns a datetime::

    What is your birthday?: 4/1/1957
    1957-04-01 00:00:00

`Get_date` is very flexible regarding how you can type times and dates. For instance, ``"April 4, 1967"``, ``"today"``,
``"1 hour from now"``, ``"9:30 am yesterday"`` and ``"noon 3 days ago"`` are all valid date values. `Cooked_input`
functions can also take a ``default`` value. For instance, using ``"today"`` as the default value will use today's
date if the user hits enter without entering a value::

    appt_date = ci.get_date(prompt="Appointment date?", default="today")
    print(appt_date.strftime("%x"))

Produces::

    Appointment date? (enter for: today):
    4/14/2018


More Convenience Functions:
---------------------------

`Cooked_input` provides several more convenience functions for getting different input types:


    +----------------+-------------------------------+
    | **Function**   |  **Return type**              |
    +================+===============================+
    | `get_string`   | string                        |
    +----------------+-------------------------------+
    | `get_int`      | int                           |
    +----------------+-------------------------------+
    | `get_float`    | float                         |
    +----------------+-------------------------------+
    | `get_date`     | datetime                      |
    +----------------+-------------------------------+
    | `get_boolean`  | boolean (`True` or `False`)   |
    +----------------+-------------------------------+
    | `get_yes_no`   | string (`"yes"` or `"no"`)    |
    +----------------+-------------------------------+

There are also convenience functions for a number of other `cooked_input` features, such as: getting lists,
choosing values from a table or showing a menu. For more information see the `convenience functions <get_input_convenience.html>`_
documentation,

.. note::

    It is easy to add support for input types not included with `cooked_input`. See the `tutorial <tutorial.html>`_ for
    examples of adding custom types (convertors) and validators.

Menus:
------

To give you a teaser of some of the further features in `Cooked_input` let's look a quick look at menus.
`Cooked_input` has a lot more functionality for menus and tables, but this will show you a little of what you
have to look forward to.

`Cooked_input` menus have two parts: a `tag` (the thing you type in to choose the menu item) and the `item data` (the
data for the menu item.) The simplest way to make a menu is to use the `get_menu` convenience function. This creates
numbered menu items for each item in a list of choices and returns the number of the item picked::

    choices = ['red', 'blue', 'green']
    result = ci.get_menu(choices)
    print('result={}'.format(result))

produces::

    1  red
    2  blue
    3  green

    Choose a table item: 1
    result=1

There are a lot of options that can be passed to `get_menu`. For instance, the `prompt` option sets the prompt string
presented to the user. Setting `default_action` to **TABLE_RETURN_FIRST_VAL** option can be used to return the choice
item_data instead of the tag::

    choices = ['red', 'blue', 'green']
    result = ci.get_menu(choices, prompt="Choose a color", default_action=ci.TABLE_RETURN_FIRST_VAL)
    print('result={}'.format(result))

produces::

    1  red
    2  blue
    3  green

    Choose a color: 1
    result=red

This just scratches the surface of what can be done with `Cooked_input` menus and tables. For more examples,
see `get_menu.py`, `get_table_input.py`, and `get_unicode.py` in the examples folder.

Further Reading:
----------------

`Cooked_input` has a lot more features and capabilities for getting, cleaning and validating inputs. `Cooked_input` also has
capabilities for user commands and data tables. To learn about the advanced capabilities of `cooked_input`,
see the `tutorial <tutorial.html>`_ and `how to <how_to.html>`_.
