"""
get_input module to get values from the command line.

Holds the machinery: the :class:`GetInput` class that does the cleaning, conversion and
validation, the commands that can be typed at a prompt, and the exceptions they raise. The
convenience functions that wrap all this -- ``get_int``, ``get_string`` and the rest -- live in
``input_convenience.py``.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017-2026
"""


from __future__ import annotations

import collections
import collections.abc
import getpass
from typing import Any

from ._typing import CleanerArg, CommandAction, CommandsArg, ErrorCallback, GetInputValidatorArg
from .error_callbacks import MaxRetriesError, ValidationError, ConvertorError
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .validators import _in_all
from .convertors import Convertor
from .input_utils import compose


# Custom exceptions for get_input
class GetInputInterrupt(KeyboardInterrupt):
    """
    A cancellation command (COMMAND_ACTION_CANCEL) occurred.
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


# Named tuple and action types for GetInput commands
CommandResponse = collections.namedtuple('CommandResponse', 'action value')

# Command action constants
COMMAND_ACTION_USE_VALUE = 'enter_value_action'
COMMAND_ACTION_CANCEL = 'cancel_input_action'
COMMAND_ACTION_NOP = 'nop_action'

COMMAND_ACTIONS = {
    COMMAND_ACTION_USE_VALUE: 'enter_value_action',
    COMMAND_ACTION_CANCEL: 'cancel_input_action',
    COMMAND_ACTION_NOP: 'nop_action',
}


class GetInputCommand(object):
    """
    `GetInputCommand` is used to create commands that can be used while getting input from :meth:`GetInput.get_input`

    :param cmd_action: callback function used to process the command
    :param cmd_dict: (optional) a dictionary of data passed to the ``cmd_action`` callback function

    Each command has a callback function (``cmd_action``) and optional data (``cmd_dict``).

    ``cmd_action`` is a callback function used for the command. The callback is called as follows

        .. py:function:: cmd_action(cmd_str, cmd_vars, cmd_dict)

          :param cmd_str: the string used to call the command
          :param cmd_vars: additional arguments for the command (i.e. the rest of string used for the command input)
          :param cmd_dict: a dictionary of additional data for processing the command (often **None**)

    Command callback functions return a a tuple containing (`COMMAND_ACTION_TYPE`, value), where the command action
    type is one of the following:

    +-------------------------------+--------------------------------------------------------------------------+
    | **Action**                    |    **Result**                                                            |
    +===============================+==========================================================================+
    | ``COMMAND_ACTION_USE_VALUE``  |  use the second value of the tuple as the input                          |
    +-------------------------------+--------------------------------------------------------------------------+
    | ``COMMAND_ACTION_CANCEL``     |  cancel the current input (raises :class:`GetInputInterrupt` exception)  |
    +-------------------------------+--------------------------------------------------------------------------+
    | ``COMMAND_ACTION_NOP``        |  do nothing - continues to ask for the input                             |
    +-------------------------------+--------------------------------------------------------------------------+

    For convenience command action callbacks can return a :class:`CommandResponse` namedtuple instance::

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

.. note::
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
    def __init__(self, cmd_action: CommandAction, cmd_dict: dict[str, Any] | None = None) -> None:
        self.cmd_action = cmd_action
        self.cmd_dict = cmd_dict

    def __call__(self, cmd_str: str, cmd_vars: str) -> CommandResponse:
        return self.cmd_action(cmd_str, cmd_vars, self.cmd_dict)

    def __repr__(self) -> str:
        return 'GetInputCommand(cmd_action={}, cmd_dict={})'.format(self.cmd_action, self.cmd_dict)


# Named tuple for return values of GetInput.process_value
ProcessValueResponse = collections.namedtuple('ProcessValueResponse', 'valid value')


class GetInput(object):
    """
    Class to get cleaned, converted, validated input from the command line. This is the central class used for
    cooked_input.

    :param cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value
    :param convertor: the `convertor <convertors.html>`_ to apply to the cleaned value
    :param validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param prompt: the string to use for the prompt. For example ``prompt="Enter your name"``
    :param required: **True** if a non-blank value is required, **False** if a blank response is OK.
        When a value is required and no ``default`` is set, a blank response is rejected like any
        other invalid value: it is reported through ``error_callback`` and counts against ``retries``.
    :param default: the default value to use if a blank string is entered. This takes precedence over
        ``required`` (i.e. a blank response will return the default value.) Typed **Any** because any
        value will do -- it is rendered with `str` for display, then run through the same cleaning,
        conversion and validation as typed input.
    :param default_str: the string to use for the default value. In general just set the ``default``
        parameter.
    :param hidden: the input typed should not be displayed. This is useful for entering passwords.
    :param retries: the maximum number of attempts to allow before raising a :class:`MaxRetriesError`
        exception. **None** (the default) allows unlimited attempts.
    :param commands: an optional dictionary of commands. See below for more details.
    :param error_callback: a callback function to call when an error is encountered. Defaults to
        :func:`print_error`
    :param convertor_error_fmt: format string to use for `convertor <convertors.html>`_ errors. Defaults to
        **DEFAULT_CONVERTOR_ERROR**. Format string receives two variables - **{value}** the value that failed
        conversion, and **{error_content}** set by the convertor.
    :param validator_error_fmt: format string to use for `validator <validators.html>`_ errors. Defaults
        to **DEFAULT_VALIDATOR_ERROR**. Format string receives two variables - **{value}** the value that
        failed conversion, and **{error_content}** set by the validator.

    :raises TypeError: if given an option this class does not have

    Every parameter from ``prompt`` onwards is keyword-only, and all of them are optional -- most calls
    use one or two. They used to be collected from a ``**options`` bag, which logged a warning for
    anything it did not recognise and then carried on with the default, so a misspelled option left the
    prompt looking almost right. Naming them means Python rejects an unknown one where it was written.

    Commands:

        :class:`GetInput` optionally takes a dictionary containing commands that can be run from the input prompt. The key for
        each command is the string used to call the command and the value is an instance of the :class:`GetInputCommand` class
        for the command. For intance, the following dictionary sets two different command string (**/?** and **/help**)
        to call a function to show help information::

            {
                "/?": GetInputCommand(show_help_action)),
                "/help": GetInputCommand(show_help_action)),
            }

        For more information see :class:`GetInputCommand`
    """
    def __init__(self, cleaners: CleanerArg = None, convertor: Convertor | None = None,
                 validators: GetInputValidatorArg = None, *,
                 prompt: str = '',
                 required: bool = True,
                 default: Any = None,
                 default_str: str | None = None,
                 hidden: bool = False,
                 retries: int | None = None,
                 commands: CommandsArg = None,
                 error_callback: ErrorCallback = print_error,
                 convertor_error_fmt: str = DEFAULT_CONVERTOR_ERROR,
                 validator_error_fmt: str = DEFAULT_VALIDATOR_ERROR) -> None:
        self.cleaners = cleaners
        self.convertor = convertor
        self.validators = validators

        # str() rather than the annotation alone: a caller may reasonably hand this an int or an
        # enum, and the prompt is only ever displayed.
        self.prompt_str = str(prompt)
        self.required = bool(required)
        # The default is displayed and then re-processed as though it had been typed, so it is
        # held as the string a user would have entered to get it.
        self.default_val = None if default is None else str(default)
        self.default_string = default_str  # get_from_table may want to display a value but return an id.
        self.hidden = hidden
        self.max_retries = retries
        self.error_callback = error_callback
        self.convertor_error_fmt = convertor_error_fmt
        self.validator_error_fmt = validator_error_fmt
        # get_input tests this with a plain truth test, so no-commands becomes an empty dict here
        # rather than leaving every use site to tell None and {} apart.
        self.commands = {} if commands is None else commands

        if self.default_val is not None:
            # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
            # logging.warning('Warning: both required and a default value specified. Blank inputs will use default value.')
            self.required = True

        if not self.default_string:
            if not self.required and not self.default_val:
                self.default_string = ' (enter to leave blank)'
            elif self.default_val:
                if self.hidden:
                    self.default_string = ' (enter for: ***)' 
                else:
                    self.default_string = ' (enter for: %s)' % self.default_val
            else:
                self.default_string = ''


    def get_input(self) -> Any:
        """
        Get input from the command line and return a validated response.

        :return: the cleaned, converted, validated input. The return type is **Any** because it
            is whatever this instance's `convertor <convertors.html>`_ produces; with no
            convertor the value comes back as the `str` that was typed.

        This method prompts the user for an input, and returns the cleaned, converted, and validated input.
        """
        retries = 0
        # Fixing: `valid_response` used to be assigned only inside the loop, so
        # retries=0 -- a loop whose body never runs -- reached the check after it with
        # the name unbound and raised UnboundLocalError instead of the MaxRetriesError
        # the caller asked for by setting a retry limit.
        valid_response = False
        input_str = '{}{}: '.format(self.prompt_str, self.default_string)
        print('')

        while (self.max_retries is None) or (retries < self.max_retries):
            if self.hidden:
                response = getpass.getpass(prompt=input_str)
            else:
                response = input(input_str)

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
            else:
                # Fixing: a blank response for a required value with no default used to
                # match none of the branches above, so retries was never incremented and
                # the loop spun forever. Blank is just another rejected value here --
                # report it, count the retry, and re-prompt, so max_retries is reachable.
                self.error_callback(self.validator_error_fmt, response, 'cannot be blank')
                retries += 1
                continue

        if valid_response:
            return converted_response
        else:
            raise MaxRetriesError('Maximum retries exceeded')


    def process_value(self, value: Any) -> ProcessValueResponse:
        """
        :param value: the value to process

        :return: Return a **ProcessValueResponse** namedtuple (valid, converted_value)

        Run a value through cleaning, conversion, and validation. This allows the same processing used
        in :meth:`GetInput.get_input` to be performed on a value. For instance, the same processing used for getting
        keyboard input can be applied to the value from a gui or web form input.

        The **ProcessValueResponse** namedtuple has elements **valid** and **value**. If the value was
        successfully cleaned, converted and validated, **valid** is True and **value** is the converted and cleaned
        value. If not, **valid** is **False**, and **value** is **None**.
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
            # Was a bare (False, None) tuple. It unpacks the same, but a caller reaching
            # for .valid or .value -- which the docstring invites -- got AttributeError
            # on exactly the failure path this branch exists to report.
            return ProcessValueResponse(False, None)

        valid_response = _in_all(converted_response, self.validators, self.error_callback, self.validator_error_fmt)

        if valid_response:
            # return (True, converted_response)
            return ProcessValueResponse(True, converted_response)

        else:
            # return (False, None)
            return ProcessValueResponse(False, None)

