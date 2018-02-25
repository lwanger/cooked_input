"""
get_input module to get values from the command line.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

from __future__ import unicode_literals

import sys
import collections
import logging
import getpass

from .error_callbacks import MaxRetriesError, ValidationError, ConvertorError
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .validators import RangeValidator, in_all, validate
from .convertors import IntConvertor, FloatConvertor, BooleanConvertor, DateConvertor
from .convertors import YesNoConvertor, ListConvertor
from .cleaners import StripCleaner
from .input_utils import compose, isstring


# Custom exceptions for get_input
class GetInputInterrupt(KeyboardInterrupt):
    """
    GetInputInterrupt is raised on a cancellation command (COMMAND_ACTION_CANCEL)
    """
    pass


class RefreshScreenInterrupt(Exception):
    """
    When raised, directs ``cooked_input`` to refresh the display. Used primarily to refresh table items.
    """
    pass


class PageUpRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the previous page in paginated tables
    """
    pass


class PageDownRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the next page in paginated tables
    """
    pass


class FirstPageRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the first page in paginated tables
    """
    pass


class LastPageRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the last page in paginated tables
    """
    pass


class UpOneRowRequest(Exception):
    """
    When raised, directs ``cooked_input`` to scroll up one row in paginated tables
    """
    pass


class DownOneRowRequest(Exception):
    """
    When raised, directs ``cooked_input`` to scroll down one row in paginated tables
    """
    pass


# Python 2/3 compatibility
if sys.version_info[0] > 2:  # For Python 3
    def raw_input(prompt_msg):
        return input(prompt_msg)


# Named tuple and action types for GetInput commands
CommandResponse = collections.namedtuple('CommandResponse', 'action value')

# Command action constants
COMMAND_ACTION_USE_VALUE = 'enter_value_action'
COMMAND_ACTION_CANCEL = 'cancel_input_action'
COMMAND_ACTION_NOP = 'nop_action'


class GetInputCommand():
    """
    :param cmd_action: callback function used to process the command
    :param cmd_dict: a dictionary of data passed to the ``cmd_action`` callback function

    :class:`GetInputCommand` is used to create commands that can be used while getting input from GetInput.get_input. Each
    command has an `action` (callback function) and optional data (cmd_dict).

    The ``cmd_action`` is a callback function used for the command. The callback is called as follows::

        def cmd_action(cmd_str, cmd_vars, cmd_dict):

    :param cmd_str: the string used to call the command
    :param cmd_vars: additional arguments for the command (i.e. the rest of the command input)
    :param cmd_dict: a dictionary of additional data for processing the command

    Command callback functions return a a tuple containing (`COMMAND_ACTION_TYPE`, value), where the command action
    type is one of the following:

    +-------------------------------+------------------------------------------------------+
    | Action                        |    Result                                            |
    +-------------------------------+------------------------------------------------------+
    | **COMMAND_ACTION_USE_VALUE**  |  use the second value of the tuple as the input      |
    +-------------------------------+------------------------------------------------------+
    | **COMMAND_ACTION_CANCEL**     |  cancel the current input (raise GetInputInterrupt)  |
    +-------------------------------+------------------------------------------------------+
    | **COMMAND_ACTION_NOP**        |  do nothing - continues to ask for the input         |
    +-------------------------------+------------------------------------------------------+

    For convenience command action callbacks can return a CommandResponse namedtuple instance::

         CommandResponse(action, value)

    The ``cmd_dict`` dictionary can be used to pass data useful in processing the command. For instance, a database
    session and the name of the user can be passed with::

        cmd_dict = {'session': db_session, 'user_name': user_name }
        lookup_user_cmd = GetInputCommand(lookup_user_action, cmd_dict)

    The following show examples of of each type of command::

        def use_color_action(cmd_str, cmd_vars, cmd_dict):
            print('Use "red" as the input value')
            return (COMMAND_ACTION_USE_VALUE, 'red')

        def cancel_action(cmd_str, cmd_vars, cmd_dict):
            return CommandResponse(COMMAND_ACTION_CANCEL, None)

        def show_help_action(cmd_str, cmd_vars, cmd_dict):
            print('Commands:')
            print('---------')
            print('/?  - show this message')
            print('/cancel - cancel this operation')
            print('/red    - use red as a value')
            print('/reverse - return the user\'s name reversed')
            return CommandResponse(COMMAND_ACTION_NOP, None)

        cmds = { '/?': GetInputCommand(show_help_action),
                 '/cancel': GetInputCommand(cancel_action),
                 '/red': GetInputCommand(use_color_action, {'color': 'red'}),
                 '/reverse': GetInputCommand(user_color_action, {'user': 'fred'}) }

        try:
            result = get_string(prompt=prompt_str, commands=cmds)
        except GetInputInterrupt:
            print('Operation cancelled (received GetInputInterrupt)')

    Nothing stops you from using ``cooked_input`` to get additional input within a command action callback. For example,
    the cancel command could be extended to confirm the user wants to cancel the current input::

        def cancel_action(cmd_str, cmd_vars, cmd_dict):
            response = get_yes_no(prompt="Are you sure you want to cancel?", default='no')

            if response == 'yes':
                print('operation cancelled!')
                return CommandResponse(COMMAND_ACTION_CANCEL, None)
            else:
                return CommandResponse(COMMAND_ACTION_NOP, None)
    """
    def __init__(self, cmd_action, cmd_dict=None):
        self.cmd_action = cmd_action
        self.cmd_dict = cmd_dict

    def __call__(self, cmd_str, cmd_vars):
        return self.cmd_action(cmd_str, cmd_vars, self.cmd_dict)

    def __repr__(self):
        return 'GetInputCommand(cmd_action={}, cmd_dict={})'.format(self.cmd_action, self.cmd_dict)


class GetInput(object):
    """
    Class to get cleaned, converted, validated input from the command line. This is the central class used for
    cooked_input.

    :param cleaners: list of cleaners to apply to clean the value
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: see below

    Options:

        **prompt**: the string to use for the prompt. For example prompt="Enter your name"

        **required**: True if a non-blank value is required, False if a blank response is OK.

        **default**: the default value to use if a blank string is entered. This takes precedence over required
            (i.e. a blank response will return the default value.)

        **default_str**: the string to use for the default value. In general just set the default option.

        **hidden**: the input typed should not be displayed. This is useful for entering passwords.

        **retries**: the maximum number of attempts to allow before raising a MaxRetriesError exception.

        **error_callback**: a callback function to call when an error is encountered. Defaults to print_error

        **convertor_error_fmt**: format string to use for convertor errors. Defaults to DEFAULT_CONVERTOR_ERROR.
            Format string receives two variables - {value} the value that failed conversion, and {error_content}
            set by the convertor.

        **validator_error_fmt**: format string to use for validator errors. Defaults to DEFAULT_VALIDATOR_ERROR.
            Format string receives two variables - {value} the value that failed conversion, and {error_content}
            set by the validator.

        **commands**: an optional dictionary of commands. See below for more details.

    Commands:

        GetInput optionally takes a dictionary containing commands that can be run from the input prompt. The key for
        each command is the string used to call the command and the value is an instance of the GetInputCommand class
        for the command (e.g. "/help": GetInputCommand(show_help_action)). For more information see :class:`GetInputCommand`
    """
    def __init__(self, cleaners=None, convertor=None, validators=None, **options):
        self.cleaners = cleaners
        self.convertor = convertor
        self.validators = validators

        self.prompt_str = ''
        self.required = True
        self.default_val = None
        self.default_string = None
        self.hidden = False
        self.max_retries = None
        self.error_callback = print_error
        self.convertor_error_fmt = DEFAULT_CONVERTOR_ERROR
        self.validator_error_fmt = DEFAULT_VALIDATOR_ERROR
        self.commands = {}

        for k, v in options.items():
            if k == 'prompt':
                self.prompt_str = '%s' % v
            elif k == 'required':
                self.required = True if v else False
            elif k == 'default':
                if v is None:
                    self.default_val = None
                else:
                    self.default_val = str(v)
            elif k == 'default_str':  # for get_from_table may want to display value but return id.
                self.default_string = v
            elif k == 'hidden':
                self.hidden = v
            elif k == 'retries':
                self.max_retries = v
            elif k == 'error_callback':
                self.error_callback = v
            elif k == 'convertor_error_fmt':
                self.convertor_error_fmt = v
            elif k == 'validator_error_fmt':
                self.validator_error_fmt = v
            elif k == 'commands':
                self.commands = v
            else:
                logging.warning('Warning: get_input received unknown option (%s)' % k)

        if self.default_val is not None:
            # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
            # logging.warning('Warning: both required and a default value specified. Blank inputs will use default value.')
            self.required = True

        if not self.default_string:
            if not self.required and not self.default_val:
                self.default_string = ' (enter to leave blank)'
            elif self.default_val:
                self.default_string = ' (enter for: %s)' % self.default_val
            else:
                self.default_string = ''


    def get_input(self):
        """
        Get input from the command line and return a validated response.

        :return: the cleaned, converted, validated input

        get_input prompts the user for an input. The input is then cleaned, converted, and validated,
        and the validated response is returned.
        """
        retries = 0
        input_str = '{}{}: '.format(self.prompt_str, self.default_string)
        print('')

        while (self.max_retries is None) or (retries < self.max_retries):
            if self.hidden:
                response = getpass.getpass(prompt=input_str)
            else:
                response = raw_input(input_str)

            if self.commands:
                command_action = None
                for cmd in self.commands:
                    if response.lstrip().startswith(cmd):
                        idx = response.find(cmd)
                        cmd_str = response[:idx+len(cmd)].strip()
                        cmd_vars = response[idx+len(cmd):].strip()
                        command_action, command_value = self.commands[cmd](cmd_str, cmd_vars)
                        break

                if command_action:
                    if command_action == COMMAND_ACTION_USE_VALUE:
                        response = command_value
                    elif command_action == COMMAND_ACTION_NOP:
                        continue
                    elif command_action == COMMAND_ACTION_CANCEL:
                        raise GetInputInterrupt
                    else:
                        raise RuntimeError('GetInput.get_input: Unknown command action specified ({})'.format(command_action))

            if not self.required and not response:
                return None
            elif self.default_val and not response:
                valid_response, converted_response = self.process_value(self.default_val)

                if valid_response:
                    return converted_response
                else:
                    raise ValidationError('default value "{!r}" did not pass validation.'.format(self.default_val))
            elif response:
                valid_response, converted_response = self.process_value(response)

                if valid_response:
                    break
                else:
                    retries += 1
                    # TODO: show validation error messages
                    continue

        if valid_response:
            return converted_response
        else:
            raise MaxRetriesError('Maximum retries exceeded')


    def process_value(self, value):
        """
        :param value: the value to process

        :return: Return a tuple of (valid, converted_value), if the values was cleaned, converted and validated successfully,
            valid is True and converted value is the converted and cleaned value. If not, valid is False, and value is None.

        Run a value through cleaning, conversion, and validation. This allows the same processing used
        in get_input to be performed on a value. For instance, the same processing used for getting
        keyboard input can be applied to the value from a gui or web form input.
        """
        if self.cleaners:
            cleaned_response = compose(value, self.cleaners)
        else:
            cleaned_response = value

        try:
            if self.convertor:
                converted_response = self.convertor(cleaned_response, self.error_callback, self.convertor_error_fmt)
            else:
                converted_response = cleaned_response
        except ConvertorError:
            return (False, None)

        valid_response = in_all(converted_response, self.validators, self.error_callback, self.validator_error_fmt)

        if valid_response:
            return (True, converted_response)
        else:
            return (False, None)


#############################
### Convenience Functions ###
#############################

def get_input(cleaners=None, convertor=None, validators=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: see GetInput for a list of value options

    :return: the cleaned, converted, validated string

    Convenience function to create a GetInput instance and call its get_input function. See
    GetInput.get_input for more details.
    """
    gi = GetInput(cleaners, convertor, validators, **options)
    return gi.get_input()


def process_value(value, cleaners=None, convertor=None, validators=None, error_callback=print_error,
            convertor_error_fmt=DEFAULT_CONVERTOR_ERROR, validator_error_fmt=DEFAULT_VALIDATOR_ERROR):
    """
    :param value: the value to process
    :param cleaners: list of cleaners to apply to clean the value
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value

    :param error_callback: see GetInput for more details
    :param convertor_error_fmt: see GetInput for more details
    :param validator_error_fmt: see GetInput for more details

    :return: the cleaned, converted validated input value.

    Convenience function to create a GetInput instance and call its process_value function. See
    GetInput.process_value for more details.
    """
    options = {}
    options['error_callback'] = error_callback
    options['convertor_error_fmt'] = convertor_error_fmt
    options['validator_error_fmt'] = validator_error_fmt

    gi = GetInput(cleaners, convertor, validators, **options)
    return gi.process_value(value)


def get_string(cleaners=(StripCleaner()), validators=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated string

    Convenience function to get a string value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter some text'

    result = GetInput(cleaners, None, validators, **new_options).get_input()
    return result


def get_int(cleaners=(StripCleaner()), validators=None, minimum=None, maximum=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param minimum: minimum value allowed. Use None (default) for no minimum value.
    :param maximum: maximum value allowed. Use None (default) for no maximum value.
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated int value

    Convenience function to get an integer value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a whole (integer) number'

    if minimum is None and maximum is None:
        val_list = validators
    else:
        irv = RangeValidator(min_val=minimum, max_val=maximum)
        if validators is None:
            val_list = irv
        elif callable(validators):
            val_list = [validators, irv]
        else:
            val_list = validators + [irv]

    result = GetInput(cleaners, IntConvertor(), val_list, **new_options).get_input()
    return result


def get_float(cleaners=(StripCleaner()), validators=None, minimum=None, maximum=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param minimum: minimum value allowed. Use None (default) for no minimum value.
    :param maximum: maximum value allowed. Use None (default) for no maximum value.
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated float value

    Convenience function to get an float value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter an real (floating point) number'

    if minimum is None and maximum is None:
        val_list = validators
    else:
        irv = RangeValidator(min_val=minimum, max_val=maximum)
        if validators is None:
            val_list = irv
        elif callable(validators):
            val_list = [validators, irv]
        else:
            val_list = validators + [irv]

    result = GetInput(cleaners, FloatConvertor(), val_list, **new_options).get_input()
    return result


def get_boolean(cleaners=(StripCleaner()), validators=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated boolean value

    Convenience function to get an Boolean value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter true or false'

    result = GetInput(cleaners, BooleanConvertor(), validators, **new_options).get_input()
    return result


def get_date(cleaners=(StripCleaner()), validators=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated date value

    Convenience function to get an date value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a date'

    result = GetInput(cleaners, DateConvertor(), validators, **new_options).get_input()
    return result


def get_yes_no(cleaners=(StripCleaner()), validators=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated yes/no value

    Convenience function to get an yes/no value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter yes or no'

    result = GetInput(cleaners, YesNoConvertor(), validators, **new_options).get_input()
    return result


def get_list(cleaners=(StripCleaner()), validators=None, value_error_str='list of values', delimiter=',',
             elem_convertor=None, elem_validators=None, **options):
    """
    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param value_error_str: the format string for the value errors (see ListConvertor)
    :param delimiter: the delimiter to use between values (see ListConvertor)
    :param elem_convertor: the Convertor to use for each element (see ListConvertor)
    :param elem_validator: the Validator to use for each element
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated list of values

    Convenience function to get a list of values.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a list of values (separated by commas)'

    error_callback = print_error
    validator_error_fmt = DEFAULT_VALIDATOR_ERROR

    for k, v in options.items():
        if k == 'error_callback':
            error_callback = v
        elif k == 'validator_error_fmt':
            validator_error_fmt = v
        elif k == 'default':
            if v is None:
                default_val = None
            else:
                if isstring(v):
                    default_val = v
                elif isinstance(v, collections.Iterable):
                    default_val = (delimiter + ' ').join(v)
                else:
                    default_val = str(v)
            new_options['default'] = default_val

    convertor = ListConvertor(value_error_str=value_error_str, delimiter=delimiter, elem_convertor=elem_convertor)
    gi = GetInput(cleaners, convertor, validators, **new_options)

    while True:
        result = gi.get_input()

        if elem_validators is None:
            break
        else:
            if all(validate(elem, elem_validators, error_callback=error_callback, validator_fmt_str=validator_error_fmt) for elem in result):
                break

    return result
