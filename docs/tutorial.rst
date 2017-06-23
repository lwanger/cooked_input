
IO Get Input Tutorial
=====================

Command line tools and terminal input are very useful. I end up writing lots of programs that get some simple input
from the user and process it. It may be a creating a report from a database or a simple text-based game. While it sounds
trivial, handling command line prompts is not easy, and the the Python standard library doesn't have anything to make
this easier. Let's start with a simple example.

The first program in an introduction to Python usually looks something like this:

::

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

Looks simple enough right? What happens when the user responds with 'a':

::

    I am thinking of a number between 1 and 10.
    Guess what number I am thinking of: a
    Traceback (most recent call last):
      File "D:/Dropbox/IO/code/cooked_input/io_get_input/test/simple_input.py", line 67, in <module>
        simple_guess()
      File "D:/Dropbox/IO/code/cooked_input/io_get_input/test/simple_input.py", line 13, in simple_guess
        guess = int(input('Guess what number I am thinking of: '))
    ValueError: invalid literal for int() with base 10: 'a'

But let's look at what it actually takes to make the input robust. Checking that the input is
valid, within the correct range, works with Python 2 and 3, etc. suddenly becomes:

::

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

And all of this for the simplest of inputs. This boiler plate code is replicated and expanded for each input from the
command line. The purpose of the cooked_input library is to make it easier to get command line input from the user. It
takes care of cleaning, converting, and validating the input. It also helps put together the prompt message and error
messages. In cooked_input, we get back to a single call to get the number for the use:

::

    guess = get_input(prompt='Enter an integer between 0 and 10', convertor=IntConvertor(),
                        validators=InRangeValidator(min_val=0, max_val=10))


Breaking down get_input:
------------------------

Let's break this `get_input` statement down. The simplest call to `get_input` is:

.. code-block:: python

    result = get_input('What is your name')

This will prompt the user for their name, and return a non-blank string. If the user types in a blank value (a zero
length string) they will be prompted to re-enter the value, until a non-zero length string is entered (note: white space/spaces
is not a zero length string!)

Let's look at a more complex example.

.. code-block:: python

    result = get_input(prompt='enter a number between 1 and 10',
        convertor=IntConvertor(),
        validators=InRangeValidator(min_val=1, max_val=None), retries=3)

* *prompt*: the string to print to prompt the user.
* *convertor*: the `Convertor` used to convert the string entered into the type of value we want. `IntConvertor`
    converts the value to an `int` (integer).
* *validators*: the `Validator` (or list of validators) used to check the entered string meets the
    criteria we want. `InRangeValidator(min_val=1, max_val=10)` makes sure the value is between `1` and `10`
    (i.e.  `0<=value<=10`). If the input doesn't pass the validation, an error message is produced, and the user
    is prompted to re-enter the value.
* *retries*: there are a number of optional parameters that get_input can take (see `get_input` for more information).
    When `retries` is specified, the user will be asked a maximum of `retries` times for the input. If no valid input
    is entered within the maximum number of times, a RuntimeError is raised.
* *result*: the cleaned, converted, validated value is returned. It's safe to use as we know it meets
    the criteria we requested.

The general flow of `get_input` is:

* Prompt the user and get the input from the keyboard
* Apply the entered string through the list of cleaners.  For example if the entered values is: `"  Yes "`, and
    `cleaners=[StripCleaner(), LowerCleaner()]` (strip, then convert to lower case), would be equivalent to the
    Python statement: `"  Yes ".strip().lower()`, which would produce `"yes"`
* Apply the convertor to the cleaned string.
* Apply the list of validators to the converted value. The converted value needs to pass all of the validators (i.e. they are AND'd together). Other combinations of validators can be achieved by using the `InAnyValidator` and `NotInValidator` validators.
* The cleaned, converted, validated value is returned.

.. note::

    The order of the cleaners and validators is maintained. For example, if the list of cleaners is `cleaners=[StripCleaner(), LowerCleaner()]`, then the strip operation is performed before conversion to lower case.

More examples:
--------------

Let's look at a few more simple examples:

To get 'yes' or 'no':

::

    get_input(prompt="Yes or no?", cleaners=StripCleaner(), convertor=YesNoConvertor(), default='Y')

Or to get from a list of choices:

::

    colors = ['red', 'green', 'blue']
    color_validator = InChoicesValidator(choices=colors)
    prompt_str = 'What is your favorite color (%s)' % ', '.join(colors)
    print(get_input(prompt=prompt_str, cleaners=[StripCleaner(), LowerCleaner()] validators=color_validator default='green'))

Or not in a set of choices

::

    bad_flavors = ['licorice', 'booger']
    not_in_choices_validator = NotInValidator(validators=InChoicesValidator(choices=bad_flavors))

    prompt_str = "Which of these is your favorite flavor jelly bean (not in: %s)?" % ', '.join(bad_flavors)
    response = get_input(prompt=prompt_str, cleaners=[StripCleaner(), LowerCleaner()], validators=not_in_choices_validator)

Or of course, composing lots of these together (get from a set of choice, but not in another set, with a default value...)

::

    good_flavors = ['cherry', 'lime', 'lemon', 'orange']
    bad_flavors = ['licorice']
    good_flavor_validator = InChoicesValidator(choices=good_flavors)
    not_in_choices_validator = NotInValidator(validators=InChoicesValidator(choices=bad_flavors))

    prompt_str = "Which of these is your favorite flavor jelly bean (%s, but not licorice!)?" % ', '.join(good_flavors)
    cleaners = [StripCleaner(), LowerCleaner()]

    validators = [good_flavor_validator, not_in_choices_validator]
    response = get_input(prompt=prompt_str, cleaners=cleaners, validators=validators, default='cherry')

There are a lot of examples in the test directory.

see TODO.md for list of TODO items
