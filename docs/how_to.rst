.. currentmodule:: cooked_input

How-to / FAQ
************


Some examples of how to....

Getting yes or no
-----------------

To get 'yes' or 'no':

.. code-block:: python

    get_yes_no()

Adding the `default` option, specifies to return 'yes' if a blank value is entered:

.. code-block:: python

    get_yes_no(default='Y')

which is equivalent to writing:

.. code-block:: python

    get_input(prompt="Enter yes or no?", cleaners=StripCleaner(), convertor=YesNoConvertor(), default='Y')

Restricting to a list of choices
--------------------------------

To get that is restricted to a value from a list of choices:

.. code-block:: python

    colors = ['red', 'green', 'blue']
    color_validator = ChoiceValidator(colors)
    prompt_str = 'What is your favorite color (%s)' % ', '.join(colors)
    result = get_input(prompt=prompt_str, cleaners=[StripCleaner(), CapitalizationCleaner(style='lower')], validators=color_validator)

.. note::

    Validator functions compare the exact value sent from the cleaned input. Without the specified cleaners in the example
    above any leading or trailing white space characters or capital letters would prevent matches on the ChoiceValidator.

Adding a `ChoiceCleaner`, allows the user to just input the first few letters of the choice (enough to differentiate
to a single choice.):

.. code-block:: python

    colors = ['red', 'green', 'blue', 'black']
    color_cleaner = ChoiceCleaner(colors)
    color_validator = ChoiceValidator(colors)
    prompt_str = 'What is your favorite color (%s)' % ', '.join(colors)
    result = get_input(prompt=prompt_str, cleaners=[StripCleaner(), CapitalizationCleaner('lower'), color_cleaner], validators=color_validator)

Typing `"r"` or `"g"` would be enough to match `red` or `green` respectively, but three letters (e.g. `"blu"`) would be
required to differentiate between `black` and `blue`.

Excluding a list of choices
---------------------------

The following example will except any string value, except `"licorice"` or `"booger"`:

.. code-block:: python

    bad_flavors = ['licorice', 'booger']
    not_in_choices_validator = NoneOfValidator(bad_flavors)

    prompt_str = "What is your favorite flavor of jelly bean (don't say: %s)?" % ' or '.join(bad_flavors)
    response = get_input(prompt=prompt_str, cleaners=[StripCleaner(), CapitalizationCleaner(style='lower')], validators=not_in_choices_validator)

.. note::

    The `AnyOf` and `NoneOf` validators can take either values or validator functions as validators. For instance, in the
    example above you could also use: not_in_choices_validator = NoneOfValidator(ChoiceValidator(bad_flavors))


Composing Multiple Validators
-----------------------------

Of course you can compose an arbitrary number of these together. For instance, to get a number from `-10` to `10`,
defaulting to `5`, and not allowing `0`:

.. code-block:: python

    prompt_str = "Enter a number between -1 and 10, but not 0"
    validators = [RangeValidator(-10, 10), NoneOfValidator(0)]
    response = get_input(prompt=prompt_str, convertor=IntConvertor(), validators=validators, default=5)

More Examples
-------------

Cooked_input has a lot more of functionality for getting input of different types (floats, Booleans, Dates, lists,
passwords, etc.), as well as lots of validators and cleaners. It also has a number of features for getting input from
tables (which is nice for working with values in database tables). There are a lot of examples in the examples directory.

TODO
----

- error callback, convertor_error_fmt and validator_error_fmt
- Menus
- Actions/callbacks/action_dicts
- TableItems/Tables
- item filters, enabled, hidden items
- pagination
- Commands

example commands::

    def user_reverse_action(cmd_str, cmd_vars, cmd_dict):
            user = cmd_dict['user']
            return (COMMAND_ACTION_USE_VALUE, user[::-1])

    def to_mm_cmd_action(cmd_str, cmd_vars, cmd_dict):
        # Convert a value from inches to mm and use the resulting value for the input
        try:
            inches = float(cmd_vars)
            return (COMMAND_ACTION_USE_VALUE, str(inches * 25.4))
        except(ValueError):
            print(f'Invalid number of inches provided to {} command.'.format(cmd_str)
            return (COMMAND_ACTION_NOP, None)

- Exceptions