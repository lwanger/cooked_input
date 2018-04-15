.. currentmodule:: cooked_input

Cooked Input Quick Start
************************

Getting started in `cooked_input` is very easy. To show how easy it is, lets build a simple application to make a
contact list.

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

The simplest usage of `cooked_input`::

    ci.get_string(prompt="What is your name?")

This will produce::

    >>> ci.get_string(prompt="What is your name?")

    What is your name?: john Cleese
    'john cleese'

This acts just like the Python `input` command (or `raw_input` in legacy Python.) Unlike `input` `cooked_input` will
keep on asking until you enter valid input. `Get_string` will not accept a blank line.

.. note::

    `Cooked_input` functions can be made to accept a blank input by adding the `required` parameter::

        ci.get_string(prompt="What is your name?", required=False)

Since we are entering a name, we want to make sure the value is capitalized. `Cooked_input` provides a number of `cleaners <cleaners.html>`_
that can be used to clean up the input value. :class:`CapitalizationCleaner` can be used to change the case of the input
value. It takes a ``style`` parameter to say how you want the value changed. In this case we want use use ``ALL_WORDS_CAP_STYLE``
to capitalize all of the words in the value::

    cap_cleaner = ci.CapitalizationCleaner(style=ci.ALL_WORDS_CAP_STYLE)
    ci.get_string(prompt="What is your name?", cleaners=[cap_cleaner])

Now it produces::

    >>> ci.get_string(prompt="What is your name?")

    What is your name?: john Cleese
    'John Cleese'

Getting Integers:
-----------------

`Cooked_input` has a number of `convenience functions <get_input_convenience.html>`_ to get different input types. Next
we use the `get_int` function to get the user's age::

    ci.get_int(prompt="How old are you?", minimum=1)

`get_int` will take input and return a whole number (i.e. an integer.) If the input cannot be converted to an integer
it will ask the user again. In addition it can take parameters for the ``minimum`` and ``maximum`` values allowed.
In this case we only allow people who are at least 1 year old. Since no ``maximum`` value is given there is no
maximum age allowed in this example::

    $ python temp.py

    How old are you?: abc
    "abc" cannot be converted to an integer number
    How old are you?: 0
    "0" too low (min_val=1)
    How old are you?: 67
    67

Getting Dates:
--------------

`get_date` is used to get a date (more specifically a datetime). Today's date is used as a ``maximum`` as the user
can't be born in the future::

    import datetime
    today = datetime.datetime.today()
    birthday = ci.get_date(prompt="What is your birthday?", maximum=today)
    print(birthday)

Running this returns a datetime::

    What is your birthday?: 4/1/1957
    1957-04-01 00:00:00

`Get_date` is very flexible on how you to type times and dates. For instance, ``April 4, 1967``, ``today`` and
``tomorrow`` are all valid date values. `Cooked_input` functions can also take a ``default`` value. For instance,
using ``"today"`` as the default value will use today's date if the user hits enter without entering a value::

    ci.get_date(prompt="Appointment datey?", default="today")

Which produces::

    Appointment date? (enter for: today):
    2018-04-13 23:07:34.920915

Further reading:
----------------

`Cooked_input` has a lot more features and capabilities for getting, cleaning and validating inputs. Additional
convenience functions can be found at `convenience functions <get_input_convenience.html>`_. `Cooked_input` also has
capabilities for user commands, menu, and data tables. To learn about the advanced capabilities of `cooked_input`,
see the `tutorial <tutorial.html>`_ and `how to <how_to.html>`_.
