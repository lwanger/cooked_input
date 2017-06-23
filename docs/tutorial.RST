
IO Get Input Tutorial
=====================

The first program in an introduction to Python usually looks something like this (adapted from
http://inventwithpython.com/chapter4.html by Al Sweigart):

.. code-block::

    import random
    guessesTaken = 0
    number = random.randint(1, 10)
    print('I am thinking of a number between 1 and 10.')
    guess = int(input('Guess what number I am thinking of: '))

    if guess < number:
        print('Buzz.... you guessed too low.')
    elif guess > number:
        print('Buzz.... you guessed too high.')
    else:
        print('Ding ding... you guessed it!')

Looks simple enough right? But let's look at what it actually takes to make this robust. Checking that the input is
valid, within the correct range, works with Python 2 and 3, etc. suddenly becomes:

.. code-block::
    def robust_guess():
    number = random.randint(1, 10)
    print('I am thinking of a number between 1 and 10.')

    while True:
        if sys.version_info.major > 2:
            result = input('Guess what number I am thinking of: ')
        else:
            result = raw_input('Guess what number I am thinking of: ')

        try:
            guess = int(result)
            if guess < 1 or guess > 10:
                print('Please enter a number between 1 and 10, try again.')
                continue
            break
        except ValueError:
            print('That is not an integer, try again.')

    if guess < number:
        print('Buzz.... you guessed too low.')
    elif guess > number:
        print('Buzz.... you guessed too high.')
    else:
        print('Ding ding... you guessed it!')

And all of this for the simplest of inputs.

document usage.
point to examples
talk about convertors, cleaners, and validators

see TODO.md for list of TODO items


Motivation
----------


Using io_get_input
------------------

.. code-block:: python

    result = get_input()