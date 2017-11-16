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

from prompt_toolkit import prompt
from prompt_toolkit.key_binding.defaults import load_key_bindings_for_prompt
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token

from .error_callbacks import MaxRetriesError, ValidationError, ConvertorError
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .validators import RangeValidator, in_all, validate
from .convertors import IntConvertor, FloatConvertor, BooleanConvertor, DateConvertor
from .convertors import YesNoConvertor, ListConvertor
from .cleaners import StripCleaner
from .input_utils import compose, isstring

# Custom exceptions for get_input
class GetInputInterrupt(KeyboardInterrupt):
    pass

class RefreshScreenInterrupt(Exception):
    pass

# prompt_toolkit stuff
default_key_registry = load_key_bindings_for_prompt(enable_abort_and_exit_bindings=True, enable_search=False,
                                                    enable_auto_suggest_bindings=False)

# registry = load_key_bindings_for_prompt()

@default_key_registry.add_binding(Keys.ControlD)
def _(event):
    raise GetInputInterrupt('Operation cancelled by user')

@default_key_registry.add_binding(Keys.Tab)
def _(event):
    event.cli.buffers['DEFAULT_BUFFER'].insert_text('\t')


# @registry.add_binding(Keys.F1)
# @default_key_registry.add_binding(Keys.F1)
# def _(event):
#     # When F1 is hit print a help message
#     def get_help_text():
#         print('F1 for help')
#     event.cli.run_in_terminal(get_help_text)


# for bottom toolbar
# def get_bottom_toolbar_text():
#     print('F1 for help, Ctrl-D to abort action')
#
# def get_bottom_toolbar_tokens(cli):
#     # return [(Token.Toolbar, ' This is a toolbar. ')]
#     return [(Token.Toolbar, ' This is a toolbar. ')]
#
# bottom_toolbar_style = style_from_dict({
#     Token.Toolbar: '#ffffff bg:#333333',
# })


# Python 2/3 compatibility
if sys.version_info[0] > 2:  # For Python 3
    # from abc import ABCMeta, abstractmethod
    def raw_input(prompt_msg):
        return input(prompt_msg)


class GetInput(object):
    def __init__(self, cleaners=None, convertor=None, validators=None, **options):
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
                required (i.e.  a blank response will return the default value.)

            default_str: the string to use for the default value. In general just set the default option.
                This is used by get_from_table to display a value but return a table id.

            hidden: the input typed should not be displayed. This is useful for entering passwords.

            retries: the maximum number of attempts to allow before raising a MaxRetriesError exception.

            error_callback: a callback function to call when an error is encountered. Defaults to print_error

            convertor_error_fmt: format string to use for convertor errors. Defaults to DEFAULT_CONVERTOR_ERROR.
                Format string receives two variables - {value} the value that failed conversion, and {error_content}
                set by the convertor.

            validator_error_fmt: format string to use for validator errors. Defaults to DEFAULT_VALIDATOR_ERROR.
                Format string receives two variables - {value} the value that failed conversion, and {error_content}
                set by the validator.

            use_prompt_toolkit: if True will use the prompt_toolkit for the input, else uses input or raw_input. For
                more details, see the prompt_toolkit documentation at: http://python-prompt-toolkit.readthedocs.io/en/stable/index.html

            key_registry: If using the prompt toolkit, key_registry defines custom key bindings.

            screen_refresh_action: screen_refresh_action is a function to call to print to the screen on a RefreshScreenInterrupt exception.
                Used to refresh tables.

            choice_refresh_action: choice_refresh_action is a function to call to change the cleaner, convertor and validator.
                Used to refresh tables.

            use_bottom_toolbar: If True will, and using prompt_toolkit, will show a bottom toolbar.

            bottom_toolbar_str: If using the bottom toolbar, this is the string used for the text.
        """
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
        self.use_prompt_toolkit = True
        self.key_registry = default_key_registry
        # refresh_action = None
        self.screen_refresh_action = None
        self.choice_refresh_action = None
        self.use_bottom_toolbar = False
        self.bottom_toolbar_str = 'Ctrl-D to abort'
        # bottom_toolbar_str = ''

        # converted_response = None
        # valid_response = None

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
            elif k == 'use_prompt_toolkit':
                self.use_prompt_toolkit = v
            elif k == 'use_bottom_toolbar':
                self.use_bottom_toolbar = v
            elif k == 'bottom_toolbar_str':
                self.bottom_toolbar_str = v
            elif k == 'key_registry':
                self.key_registry = v
            # elif k == 'refresh_action':
            #     if not callable(v):
            #         raise RuntimeError("get_input: refresh_action must be a callable")
            #     refresh_action = v
            elif k == 'screen_refresh_action':
                if not callable(v):
                    raise RuntimeError("get_input: screen_refresh_action must be a callable")
                self.screen_refresh_action = v
            elif k == 'choice_refresh_action':
                if not callable(v):
                    raise RuntimeError("get_input: choice_refresh_action must be a callable")
                self.choice_refresh_action = v
            else:
                logging.warning('Warning: get_input received unknown option (%s)' % k)

        if self.default_val is not None and not self.default_string:
            self.default_string = str(self.default_val)

        # if not required and default_val is not None:
        if self.default_val is not None:
            # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
            # logging.warning('Warning: both required and a default value specified. Blank inputs will use default value.')
            required = True

        if not self.required and not self.default_val:
            default_string = ' (enter to leave blank)'
        elif self.default_val:
            self.default_string = ' (enter for: %s)' % self.default_string
        else:
            self.default_string = ''


    def _get_from_prompt_toolkit_prompt(self, input_str):
        if self.use_bottom_toolbar is True:
            bottom_toolbar_tokens = lambda x: [(Token.Toolbar, self.bottom_toolbar_str)]
            bottom_toolbar_style = style_from_dict({Token.Toolbar: '#ffffff bg:#333333'})
            response = prompt(input_str, is_password=self.hidden, key_bindings_registry=self.key_registry,
                              get_bottom_toolbar_tokens=bottom_toolbar_tokens, style=bottom_toolbar_style)
        else:
            response = prompt(input_str, patch_stdout=True, is_password=self.hidden, key_bindings_registry=self.key_registry)

        return response


    def get_input(self):
        """
        Get input from the command line and return a validated response.

        get_input prompts the user for an input. The input is then cleaned, converted, and validated,
        and the validated response is returned.

        :param options:  see above
        :return: the cleaned, converted, validated input
        """
        retries = 0
        #input_str = '{}{}: '.format(self.prompt_str, self.default_string)
        input_str = '{}: '.format(self.prompt_str)
        print('')

        while (self.max_retries is None) or (retries < self.max_retries):
            if self.use_prompt_toolkit is True:
                response = self._get_from_prompt_toolkit_prompt(input_str)
            else:
                if self.hidden:
                    response = getpass.getpass(prompt=input_str)
                else:
                    response = raw_input(input_str)

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


class GetTableInput(GetInput):
    def __init__(self, table, cleaners=None, convertor=None, validators=None, **options):
        # TODO - move to get_menu / get_table?
        # TODO - clean up options and process GetTableInput specific options
        # TODO - document
        self.table = table
        super(GetTableInput, self).__init__(cleaners, convertor, validators, **options)


    def get_input(self):
        retries = 0
        input_str = '{}{}: '.format(self.prompt_str, self.default_string)
        print('')

        while (self.max_retries is None) or (retries < self.max_retries):
            try:
                response = use_prompt_toolkit_application(input_str, self.hidden, self.key_registry)

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
            except (RefreshScreenInterrupt):
                # if refresh_action is not None:
                #     refresh_action()
                if self.screen_refresh_action is not None:
                    self.screen_refresh_action()
                if self.choice_refresh_action is not None:
                    table_choices, cleaners, convertor, validators = self.choice_refresh_action()

        if valid_response:
            return converted_response
        else:
            raise MaxRetriesError('Maximum retries exceeded')



# get_input stuff
# def process(value, cleaners=None, convertor=None, validators=None, error_callback=print_error,
#             convertor_error_fmt=DEFAULT_CONVERTOR_ERROR, validator_error_fmt=DEFAULT_VALIDATOR_ERROR):
#     """
#     runs a value through cleaning, conversion, and validation. This allows the same processing used
#     in get_input to be performed on a value. For instance, the same processing used for getting
#     keyboard input can be applied to the value from a gui or web form input.
#
#     :param value: the value to process
#     :param cleaners: list of cleaners to apply to clean the value
#     :param convertor: the convertor to apply to the cleaned value
#     :param validators: list of validators to apply to validate the cleaned and converted value
#     :param error_callback: the function to call when an error occurs in conversion or validation
#     :param convertor_error_fmt: format string fro convertor errors (defaults to DEFAULT_CONVERTOR_ERROR)
#     :param validator_error_fmt: format string fro validator errors (defaults to DEFAULT_VALIDATOR_ERROR)
#
#     :return: Return of tuple (valid, converted_value), if the values was cleaned, converted and validated successfully,
#         valid is True and converted value is the converted and cleaned value. If not, valid is False, and value is None.
#     """
#     if cleaners:
#         cleaned_response = compose(value, cleaners)
#     else:
#         cleaned_response = value
#
#     try:
#         if convertor:
#             converted_response = convertor(cleaned_response, error_callback, convertor_error_fmt)
#         else:
#             converted_response = cleaned_response
#     except ConvertorError:
#         return (False, None)
#
#     valid_response = in_all(converted_response, validators, error_callback, validator_error_fmt)
#
#     if valid_response:
#         return (True, converted_response)
#     else:
#         return (False, None)

# def get_from_prompt_toolkit_prompt(input_str, hidden, key_registry, use_bottom_toolbar, bottom_toolbar_str):
#     if use_bottom_toolbar is True:
#         bottom_toolbar_tokens = lambda x: [(Token.Toolbar, bottom_toolbar_str)]
#         bottom_toolbar_style = style_from_dict({Token.Toolbar: '#ffffff bg:#333333'})
#         response = prompt(input_str, is_password=hidden, key_bindings_registry=key_registry,
#                           get_bottom_toolbar_tokens=bottom_toolbar_tokens, style=bottom_toolbar_style)
#     else:
#         # response = prompt(input_str, is_password=hidden, key_bindings_registry=key_registry)
#         response = prompt(input_str, patch_stdout=True, is_password=hidden, key_bindings_registry=key_registry)
#
#     return response

from prompt_toolkit.layout.containers import Window, VSplit
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.interface import Application, CommandLineInterface
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.key_binding.manager import KeyBindingManager, Registry
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import LayoutDimension


def use_prompt_toolkit_application(ptable, prompt_str, hidden, key_registry):
    # Use the prompt toolkit to get table input using a split layout
    # not using hidden yet
    # not using key_registry yet
    buffers = {
        'DEFAULT_BUFFER': Buffer(is_multiline=True),
        'PROMPT_STR_BUFFER': Buffer(is_multiline=True),
        'TABLE': Buffer(is_multiline=True),
    }
    buffers['TABLE'].text = ptable.table.get_string()
    buffers['PROMPT_STR_BUFFER'].text = prompt_str

    manager = KeyBindingManager()
    registry = manager.registry
    # register_table_keys(registry)
    # print(ptable.table.get_string())

    table_layout = Window(height=LayoutDimension.exact(26), content=BufferControl(buffer_name='TABLE'))
    prompt_str_layout = Window(width=LayoutDimension.exact(len(prompt_str) + 1), height=LayoutDimension.exact(3),
                               content=BufferControl(buffer_name='PROMPT_STR_BUFFER'))
    prompt_input_layout = Window(height=LayoutDimension.exact(3), content=BufferControl(buffer_name='DEFAULT_BUFFER'))
    prompt_line_layout = VSplit(children=[prompt_str_layout, prompt_input_layout])
    layout = HSplit(children=[table_layout, prompt_line_layout])

    try:
        loop = create_eventloop()
        application = Application(key_bindings_registry=registry, layout=layout, buffers=buffers,
                                  use_alternate_screen=True)
        cli = CommandLineInterface(application=application, eventloop=loop)
        response = cli.run()
        # print('result={}'.format(response))
    finally:
        loop.close()

    # if do_action:
    #     return self.do_action()
    # else:
    #     return response
    return response


if False:
    def get_input(cleaners=None, convertor=None, validators=None, **options):
        """
        Get input from the command line and return a validated response.

        get_input prompts the user for an input. The input is then cleaned, converted, and validated,
        and the validated response is returned.

        Options:

            prompt: the string to use for the prompt. For example prompt="Enter your name"

            required: True if a non-blank value is required, False if a blank response is OK.

            default: the default value to use if a blank string is entered. This takes precedence over
                required (i.e.  a blank response will return the default value.)

            default_str: the string to use for the default value. In general just set the default option.
                This is used by get_from_table to display a value but return a table id.

            hidden: the input typed should not be displayed. This is useful for entering passwords.

            retries: the maximum number of attempts to allow before raising a MaxRetriesError exception.

            error_callback: a callback function to call when an error is encountered. Defaults to print_error

            convertor_error_fmt: format string to use for convertor errors. Defaults to DEFAULT_CONVERTOR_ERROR.
                Format string receives two variables - {value} the value that failed conversion, and {error_content}
                set by the convertor.

            validator_error_fmt: format string to use for validator errors. Defaults to DEFAULT_VALIDATOR_ERROR.
                Format string receives two variables - {value} the value that failed conversion, and {error_content}
                set by the validator.

            use_prompt_toolkit: if True will use the prompt_toolkit for the input, else uses input or raw_input. For
                more details, see the prompt_toolkit documentation at: http://python-prompt-toolkit.readthedocs.io/en/stable/index.html

            key_registry: If using the prompt toolkit, key_registry defines custom key bindings.

            screen_refresh_action: screen_refresh_action is a function to call to print to the screen on a RefreshScreenInterrupt exception.
                Used to refresh tables.

            choice_refresh_action: choice_refresh_action is a function to call to change the cleaner, convertor and validator.
                Used to refresh tables.

            use_bottom_toolbar: If True will, and using prompt_toolkit, will show a bottom toolbar.

            bottom_toolbar_str: If using the bottom toolbar, this is the string used for the text.


        :param cleaners: list of cleaners to apply to clean the value
        :param convertor: the convertor to apply to the cleaned value
        :param validators: list of validators to apply to validate the cleaned and converted value
        :param options:  see above
        :return: the cleaned, converted, validated input
        """

        prompt_str = ''
        required = True
        default_val = None
        default_string = None
        hidden = False
        max_retries = None
        error_callback = print_error
        convertor_error_fmt = DEFAULT_CONVERTOR_ERROR
        validator_error_fmt = DEFAULT_VALIDATOR_ERROR
        use_prompt_toolkit = True
        key_registry = default_key_registry
        # refresh_action = None
        screen_refresh_action = None
        choice_refresh_action = None
        use_bottom_toolbar = False
        bottom_toolbar_str = 'Ctrl-D to abort'
        # bottom_toolbar_str = ''

        converted_response = None
        valid_response = None

        for k, v in options.items():
            if k == 'prompt':
                prompt_str = '%s' % v
            elif k == 'required':
                required = True if v else False
            elif k == 'default':
                if v is None:
                    default_val = None
                else:
                    default_val = str(v)
            elif k == 'default_str':  # for get_from_table may want to display value but return id.
                default_string = v
            elif k == 'hidden':
                hidden = v
            elif k == 'retries':
                max_retries = v
            elif k == 'error_callback':
                error_callback = v
            elif k == 'convertor_error_fmt':
                convertor_error_fmt = v
            elif k == 'validator_error_fmt':
                validator_error_fmt = v
            elif k == 'use_prompt_toolkit':
                use_prompt_toolkit = v
            elif k == 'use_bottom_toolbar':
                use_bottom_toolbar = v
            elif k == 'bottom_toolbar_str':
                bottom_toolbar_str = v
            elif k == 'key_registry':
                key_registry = v
            # elif k == 'refresh_action':
            #     if not callable(v):
            #         raise RuntimeError("get_input: refresh_action must be a callable")
            #     refresh_action = v
            elif k == 'screen_refresh_action':
                if not callable(v):
                    raise RuntimeError("get_input: screen_refresh_action must be a callable")
                screen_refresh_action = v
            elif k == 'choice_refresh_action':
                if not callable(v):
                    raise RuntimeError("get_input: choice_refresh_action must be a callable")
                choice_refresh_action = v
            else:
                logging.warning('Warning: get_input received unknown option (%s)' % k)

        if default_val is not None and not default_string:
            default_string = str(default_val)

        # if not required and default_val is not None:
        if default_val is not None:
            # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
            # logging.warning('Warning: both required and a default value specified. Blank inputs will use default value.')
            required = True

        if not required and not default_val:
            default_string = ' (enter to leave blank)'
        elif default_val:
            default_string = ' (enter for: %s)' % default_string
        else:
            default_string = ''

        retries = 0
        input_str = '{}{}: '.format(prompt_str, default_string)
        print('')

        use_prompt_toolkit_application = True   # TODO -- remove me!

        while (max_retries is None) or (retries < max_retries):
            try:
                if use_prompt_toolkit is True:
                    response = get_from_prompt_toolkit_prompt(input_str, hidden, key_registry, use_bottom_toolbar, bottom_toolbar_str)

                # if use_bottom_toolbar is True:
                    #     bottom_toolbar_tokens = lambda x: [(Token.Toolbar, bottom_toolbar_str)]
                    #     bottom_toolbar_style = style_from_dict({Token.Toolbar: '#ffffff bg:#333333'})
                    #     response = prompt(input_str, is_password=hidden, key_bindings_registry=key_registry,
                    #                       get_bottom_toolbar_tokens=bottom_toolbar_tokens, style=bottom_toolbar_style)
                    # else:
                    #     # response = prompt(input_str, is_password=hidden, key_bindings_registry=key_registry)
                    #     response = prompt(input_str, patch_stdout=True, is_password=hidden, key_bindings_registry=key_registry)
                elif use_prompt_toolkit_application:
                    response = use_prompt_toolkit_application(input_str, hidden, key_registry)
                else:
                    if hidden:
                        response = getpass.getpass(prompt=input_str)
                    else:
                        response = raw_input(input_str)

                if not required and not response:
                    return None
                elif default_val and not response:
                    valid_response, converted_response = process(default_val, cleaners, convertor, validators,
                                                                 error_callback, convertor_error_fmt, validator_error_fmt)
                    if valid_response:
                        return converted_response
                    else:
                        raise ValidationError('default value "{!r}" did not pass validation.'.format(default_val))
                elif response:
                    valid_response, converted_response = process(response, cleaners, convertor, validators,
                                                                 error_callback, convertor_error_fmt, validator_error_fmt)

                    if valid_response:
                        break
                    else:
                        retries += 1
                        # print('TODO: get validation error messages')
                        continue
            except (RefreshScreenInterrupt):
                # if refresh_action is not None:
                #     refresh_action()
                if screen_refresh_action is not None:
                    screen_refresh_action()
                if choice_refresh_action is not None:
                    table_choices, cleaners, convertor, validators = choice_refresh_action()

        if valid_response:
            return converted_response
        else:
            raise MaxRetriesError('Maximum retries exceeded')
else:
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


def get_table_input(table=None, do_action=True, **options):
    """
    Get input value from a table of values. Allow to type in and return either the id or the value 
    for the choice. Useful for entering values from database tables.

    options:

        input_value: TABLE_VALUE (or True) to input the value from the table row, TABLE_ID (or False) 
            to enter the id. TABLE_ID_OR_VALUE  allows entering either and will give the preference
            to entering the value.

        return_value: TABLE_VALUE (or True) to return the value from the table row, TABLE_ID (or
            False) to return the id.

        show_table: will print the table before asking for the prompt
            before asking for the input.

        sort_by_value: whether to sort the table rows by value (True) or id (False). Defaults to sort by id.
        default: the default value to use.

        All additional get_input options are also supported (see above.)

    :param table: list of tuples, with each tuple being: (id, value) for the items in the table.
    :param cleaners: list of cleaners to apply to the inputted value.
    :param convertor: the convertor to apply to the cleaned input value.
    :param validators: list of validators to apply to the cleaned, converted input value.
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated input value. This is an id or value from the table depending on input_value.
    """
    return table.get_table_choice(do_action, **options)



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

    result = get_input(cleaners=cleaners, convertor=None, validators=validators, **new_options)
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

    result = get_input(cleaners, convertor=IntConvertor(), validators=val_list, **new_options)
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

    result = get_input(cleaners, convertor=FloatConvertor(), validators=val_list, **new_options)
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

    result = get_input(cleaners, convertor=BooleanConvertor(), validators=validators, **new_options)
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

    result = get_input(cleaners, convertor=DateConvertor(), validators=validators, **new_options)
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

    result = get_input(cleaners, convertor=YesNoConvertor(), validators=validators, **new_options)
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
                    default_val = (delimiter+' ').join(v)
                else:
                    default_val = str(v)
            new_options['default'] = default_val

    while True:
        result = get_input(cleaners, convertor=ListConvertor(value_error_str=value_error_str, delimiter=delimiter,
                            elem_convertor=elem_convertor), validators=validators, **new_options)

        if elem_validators is None:
            break
        else:
            if all(validate(elem, elem_validators, error_callback=error_callback, validator_fmt_str=validator_error_fmt) for elem in result):
                break

    return result
