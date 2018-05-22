.. currentmodule:: cooked_input

Cooked Input Tutorial
*********************

.. note::

    This tutorial is out of date. The introduction is still valid, but the rest needs to be re-written for v0.3+. The
    new tutorial discusses: The GetInput class, table, commands.

Introduction:
=============

Command line tools and terminal input are very useful. I end up writing lots of programs that get some simple input
from the user and process it. It may be a creating a report from a database or a simple text-based game. While it sounds
trivial, handling all of the exceptions and corner cases of command line input is not easy, and the Python standard
library doesn't have anything to make it easier. Let's start with a simple example.

The first program in an introduction to Python usually looks something like this::

    import random
    number = random.randint(1, 10)
    print('I am thinking of a number between 1 and 10.')
    guess = int(input('Guess what number I am thinking of: '))

    if guess < number:
        print('Buzz.... you guessed too low.')
    elif guess > number:
        print('Buzz.... you guessed too high.')
    else:
        print('Ding ding... you guessed it!')

Looks simple enough right? What happens when the user responds with 'a'::

    I am thinking of a number between 1 and 10.
    Guess what number I am thinking of: a
    Traceback (most recent call last):
      File "C:/apps/simple_input.py", line 67, in <module>
        simple_guess()
      File "C:/apps/simple_input.py", line 13, in simple_guess
        guess = int(input('Guess what number I am thinking of: '))
    ValueError: invalid literal for int() with base 10: 'a'

Let's look at what it takes to make the input robust. Checking that the input is: a number,
within the correct range, works with legacy Python (ie. version 2) and 3, etc. becomes::

        while True:
            if sys.version_info.major > 2:
                result = input('Guess what number I am thinking of: ')
            else:
                result = raw_input('Guess what number I am thinking of: ')

            try:
                guess = int(result)
                if guess < 1 or guess > 10:
                    print('not between 1 and 10, try again.')
                    continue
                break
            except ValueError:
                print('That is not an integer, try again.')

That's a lot of code to handle the simplest of inputs. This boiler plate code is replicated and expanded for each input from the
command line. Just think of how much code you would need to get and validate a new password from a user --
making sure the input is hidden, doesn't match the previous password, is at least 8 characters long,
has at least 2 upper case letters, has at least 2 punctuation marks, has at least 1 number, doesn't use the characters '[', ']', or '&', and
exits after 3 failed attempts.

The purpose of the cooked_input module is to make it easier to get command line input from the user. It
takes care of cleaning, converting, and validating the input. It also helps put together the prompt message and error
messages. In cooked_input, safely getting the value from the user in the guessing game becomes::

    guess = get_int(prompt='Guess what number I am thinking of', minimum=0, maximum=10)

For a complete listing of the guessing game code using cooked_input, see simple_input.py in the examples directory.

In case your curious, the password example above can be written in cooked_input as::

    good_password = PasswordValidator(min_len=8, min_upper=2, min_digits=1, min_puncts=2, disallowed='[]&')
    not_last_password = NoneOfValidator(EqualToValidator(old_password))
    password = get_input(prompt='Enter a new password', validators=[good_password, not_last_password], hidden=True, retries=3)


Breaking down get_input:
========================

The centerpoint of cooked_input is a function called `get_input`. In the guessing game we used a call to `get_int` which is
just a friendly wrapper around get_input that automatically fills in some of the values required to get an integer.
Similarly, all of the other convenience functions (such as `get_float`, `get_boolean`, `get_date`, etc.) are just wrappers
around get_input too.

The simplest call to `get_input` is:

.. code-block:: python

    result = get_input('What is your name')

This will prompt the user for their name and return a non-blank string. If the user types in a blank value (a zero
length string) they will receive an error message and be prompted to re-enter the value until a non-zero length string
is entered (note: white space/spaces is not a zero length string!)

Let's look at a more complicated example. The get_int call in the guessing game makes a call to get_input that looks
something like this:

.. code-block:: python

    result = get_input(prompt='Guess what number I am thinking of',
        convertor=IntConvertor(),
        validators=RangeValidator(min_val=1, max_val=None), retries=3)

* *prompt*: the string to print to prompt the user.

* *convertor*: the `Convertor` is called to convert the string entered into the type of value we want. `IntConvertor`
  converts the value to an integer (`int`).

* *validators*: the `Validator` function (or list of `Validator` functions) used to check the entered string meets the
  criteria we want. If the input doesn't pass the validation, an error message is produced, and the user is prompted to
  re-enter a value.

  `RangeValidator` takes a minimum and maximum value and checks that the input value is in the
  interval between the two. For example,  `RangeValidator(min_val=1, max_val=10)` would make sure the value is between
  `1` and `10`. (i.e. `1<=value<=10`). In the case above, `max_val` is set to `None`, so no maximum value is applied
  (i.e. checks `1<=value`)

* *options*: there are a number of optional parameters that get_input can take (see `get_input` for more information).
  By default, get_input will keep asking for values until a valid value is entered. The `retries` option specifies the
  maximum number of times to ask. If no valid input is entered within the maximum number of tries a MaxRetriesError is raised.

* *return value*: the cleaned, converted, validated value is returned. The returned value is safe to use as we know it
  meets all the criteria we requested.

The general flow of `get_input` is:

1) Prompt the user and get the input from the keyboard (sys.stdin)

2) Apply the entered string through the specified cleaners.

3) Apply the convertor to the cleaned string.

4) Apply the specified validators to the converted value. The converted value needs to pass all of the validators (i.e.
   they are AND'd together). Other combinations of validators can be achieved by using the `AnyOfValidator` (OR)
   and `NoneOfValidator` (NOT) validators.

5) Return the cleaned, converted, validated value.

.. note::

    The order of the cleaners and validators is maintained. For example, if the list of cleaners is
    `cleaners=[StripCleaner(), CapitalizationCleaner(style='lower')]`, then the strip operation is performed before
    conversion to lower case. Applying these cleaners to the value `"  Yes "` is equivalent to the Python
    statement: `"  Yes ".strip().lower()` (strip, then convert to lower case), which would produce the cleaned value: `"yes"`

.. note::

    The `process` function take an input value as a parameter and runs all of the `get_input` processing steps on
    the value (i.e. runs steps 2--5 above.) This is useful for applying the same cooked_input cleaning, conversion and
    validation to value from GUI forms, web forms or for data cleaning. The `validate_tk` example shows how
    `process` can be used to validate an input in a GUI.
