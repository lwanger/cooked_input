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
    pass


# Python 2/3 compatibility
if sys.version_info[0] > 2:  # For Python 3
    def raw_input(prompt_msg):
        return input(prompt_msg)


# Named tuple and action types for GetInput commands:
CommandResponse = collections.namedtuple('CommandResponse', 'action value')

# Command action constants
COMMAND_ACTION_USE_VALUE = 'enter_value_action'
COMMAND_ACTION_CANCEL = 'cancel_input_action'
COMMAND_ACTION_NOP = 'nop_action'


class GetInputCommand():
    """
    Used to create commands that can be used in GetInput. Each command has an action and optional data dictionary
    (cmd_dict). The cmd_dict dictionary can be used to pass data to the command. For instance, a database session or
    the name of the user can be passed: cmd_dist = {'session': db_session, 'user': user }

    The cmd_action is a callback funtion used for the command. It receives the string for the command, the
    arguments (the rest of the command input), and cmd_dict as input and returns a tuple
     containing (COMMAND_ACTION_TYPE, value), where the command action type is one of the following:

    +-------------------------------+-----------------------------------------------------------------+
    | Action                        |    Result                                                       |
    +-------------------------------+-----------------------------------------------------------------+
    | COMMAND_ACTION_USE_VALUE      |  use the second value of the tuple as the input                 |
    +-------------------------------+-----------------------------------------------------------------+
    | COMMAND_ACTION_CANCEL         |  cancel the current input (raise a GetInputInterrupt exception) |
    +-------------------------------+-----------------------------------------------------------------+
    | COMMAND_ACTION_NOP            |  do nothing - continues to ask for the input                    |
    +-------------------------------+-----------------------------------------------------------------+

    For example, the following input specifies one of each type of command::

        def use_color_action(cmd_str, cmd_vars, cmd_dict):
            return (ci.COMMAND_ACTION_USE_VALUE, cmd_dict['color'])

        def cancel_action(cmd_str, cmd_vars, cmd_dict):
            print('CANCELLING OPERATION')
            return (ci.COMMAND_ACTION_CANCEL, None)

        def show_help_action(cmd_str, cmd_vars, cmd_dict):
            print('Help Message:')
            print('-------------')
            print('/?  - show this message')
            print('/cancel - cancel this operation')
            print('/red    - use red as a value')
            return (ci.COMMAND_ACTION_NOP, None)

        cmds = { '/?': ci.GetInputCommand(show_help_action),
                 '/cancel': ci.GetInputCommand(cancel_action),
                 '/red': ci.GetInputCommand(use_color_action, {'color': 'red'}) }

        try:
            result = ci.get_string(prompt=prompt_str, commands=cmds)
        except ci.GetInputInterrupt:
            print('Got GetInputInterrupt')
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
    Class to get cleaned, converted, validated input from the command line.

    :param cleaners: list of cleaners to apply to clean the value
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options:

    Options:

        prompt: the string to use for the prompt. For example prompt="Enter your name"

        required: True if a non-blank value is required, False if a blank response is OK.

        default: the default value to use if a blank string is entered. This takes precedence over
            required (i.e. a blank response will return the default value.)

        default_str: the string to use for the default value. In general just set the default option.

        hidden: the input typed should not be displayed. This is useful for entering passwords.

        retries: the maximum number of attempts to allow before raising a MaxRetriesError exception.

        error_callback: a callback function to call when an error is encountered. Defaults to print_error

        convertor_error_fmt: format string to use for convertor errors. Defaults to DEFAULT_CONVERTOR_ERROR.
            Format string receives two variables - {value} the value that failed conversion, and {error_content}
            set by the convertor.

        validator_error_fmt: format string to use for validator errors. Defaults to DEFAULT_VALIDATOR_ERROR.
            Format string receives two variables - {value} the value that failed conversion, and {error_content}
            set by the validator.

        commands: a dictionary containing commands that can be run from the input prompt. The key for each command
            is the string used to call the command and the value is an instance of the GetInputCommand class for
             the command (e.g. "/help": GetInputCommand(show_help_action)).
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

        #if self.default_val is not None and not self.default_string:
        #    self.default_string = str(self.default_val)

        # if not required and default_val is not None:
        if self.default_val is not None:
            # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
            # logging.warning('Warning: both required and a default value specified. Blank inputs will use default value.')
            required = True

        if not self.default_string:
            if not self.required and not self.default_val:
                self.default_string = ' (enter to leave blank)'
            elif self.default_val:
                #self.default_string = ' (enter for: %s)' % self.default_string
                self.default_string = ' (enter for: %s)' % self.default_val
            else:
                self.default_string = ''


    def get_input(self):
        """
        Get input from the command line and return a validated response.

        get_input prompts the user for an input. The input is then cleaned, converted, and validated,
        and the validated response is returned.

        :return: the cleaned, converted, validated input
        """
        retries = 0
        input_str = '{}{}: '.format(self.prompt_str, self.default_string)
        print('')

        while (self.max_retries is None) or (retries < self.max_retries):
            if self.hidden:
                response = getpass.getpass(prompt=input_str)
            else:
                response = raw_input(input_str)

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
                    # print('TODO: get validation error messages')
                    continue

        if valid_response:
            return converted_response
        else:
            raise MaxRetriesError('Maximum retries exceeded')


    def process_value(self, value):
        """
            runs a value through cleaning, conversion, and validation. This allows the same processing used
            in get_input to be performed on a value. For instance, the same processing used for getting
            keyboard input can be applied to the value from a gui or web form input.

            :param value: the value to process

            :return: Return of tuple (valid, converted_value), if the values was cleaned, converted and validated successfully,
                valid is True and converted value is the converted and cleaned value. If not, valid is False, and value is None.
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


# class GetTableInput(GetInput):
#     """
#     Class to get cleaned, converted, validated input from a table of values. This can be used for data tables or menu.
#
#     :param table: a Table instance containing the data items
#     :param cleaners: list of cleaners to apply to clean the value
#     :param convertor: the convertor to apply to the cleaned value
#     :param validators: list of validators to apply to validate the cleaned and converted value
#     :param options:
#
#
#     """
#
#     def __init__(self, table, cleaners=None, convertor=None, validators=None, **options):
#
#         # TODO - move to get_menu / get_table?
#         # TODO - clean up options and process GetTableInput specific options
#         # TODO - document
#         self.table = table
#         super(GetTableInput, self).__init__(cleaners, convertor, validators, **options)


    # def get_input(self):
    #     retries = 0
    #     input_str = '{}{}: '.format(self.prompt_str, self.default_string)
    #     print('')
    #
    #     while (self.max_retries is None) or (retries < self.max_retries):
    #         try:
    #             response = use_prompt_toolkit_application(input_str, self.hidden, self.key_registry)
    #
    #             if not self.required and not response:
    #                 return None
    #             elif self.default_val and not response:
    #                 valid_response, converted_response = self.process_value(self.default_val)
    #
    #                 if valid_response:
    #                     return converted_response
    #                 else:
    #                     raise ValidationError('default value "{!r}" did not pass validation.'.format(self.default_val))
    #             elif response:
    #                 valid_response, converted_response = self.process_value(response)
    #
    #                 if valid_response:
    #                     break
    #                 else:
    #                     retries += 1
    #                     # print('TODO: get validation error messages')
    #                     continue
    #         except (RefreshScreenInterrupt):
    #             # if refresh_action is not None:
    #             #     refresh_action()
    #             if self.screen_refresh_action is not None:
    #                 self.screen_refresh_action()
    #             if self.choice_refresh_action is not None:
    #                 table_choices, cleaners, convertor, validators = self.choice_refresh_action()
    #
    #     if valid_response:
    #         return converted_response
    #     else:
    #         raise MaxRetriesError('Maximum retries exceeded')


def get_input(cleaners=None, convertor=None, validators=None, **options):
    gi = GetInput(cleaners, convertor, validators, **options)
    return gi.get_input()


def process(value, cleaners=None, convertor=None, validators=None, error_callback=print_error,
            convertor_error_fmt=DEFAULT_CONVERTOR_ERROR, validator_error_fmt=DEFAULT_VALIDATOR_ERROR):
    options = {}
    options['error_callback'] = error_callback
    options['convertor_error_fmt'] = convertor_error_fmt
    options['validator_error_fmt'] = validator_error_fmt

    gi = GetInput(cleaners, convertor, validators, **options)
    return gi.process_value(value)


#############################
### Convenience Functions ###
#############################

def get_string(cleaners=(StripCleaner()), validators=None, **options):
    """
    Convenience function to get a string value.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated string
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter some text'

    result = GetInput(cleaners, None, validators, **new_options).get_input()
    return result


def get_int(cleaners=(StripCleaner()), validators=None, minimum=None, maximum=None, **options):
    """
    Convenience function to get an integer value.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param minimum: minimum value allowed. Use None (default) for no minimum value.
    :param maximum: maximum value allowed. Use None (default) for no maximum value.
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated int value
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
    Convenience function to get an float value.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param minimum: minimum value allowed. Use None (default) for no minimum value.
    :param maximum: maximum value allowed. Use None (default) for no maximum value.
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated float value
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
    Convenience function to get an Boolean value.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated boolean value
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter true or false'

    result = GetInput(cleaners, BooleanConvertor(), validators, **new_options).get_input()
    return result


def get_date(cleaners=(StripCleaner()), validators=None, **options):
    """
    Convenience function to get an date value.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated date value
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a date'

    result = GetInput(cleaners, DateConvertor(), validators, **new_options).get_input()
    return result


def get_yes_no(cleaners=(StripCleaner()), validators=None, **options):
    """
    Convenience function to get an yes/no value.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated yes/no value
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter yes or no'

    result = GetInput(cleaners, YesNoConvertor(), validators, **new_options).get_input()
    return result


def get_list(cleaners=(StripCleaner()), validators=None, value_error_str='list of values', delimiter=',',
             elem_convertor=None, elem_validators=None, **options):
    """
    Convenience function to get a list of values.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param value_error_str: the format string for the value errors (see ListConvertor)
    :param delimiter: the delimiter to use between values (see ListConvertor)
    :param elem_convertor: the Convertor to use for each element (see ListConvertor)
    :param elem_validator: the Validator to use for each element
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated list of values
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
