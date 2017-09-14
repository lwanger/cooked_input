"""
get_input module to get values from the command line.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
import copy
import logging
import getpass

from .error_callbacks import MaxRetriesError, ValidationError, ConvertorError
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .validators import RangeValidator, ChoiceValidator, in_all
from .convertors import TableConvertor, IntConvertor, FloatConvertor, BooleanConvertor, DateConvertor
from .convertors import YesNoConvertor, ListConvertor
from .cleaners import StripCleaner
from .input_utils import compose, make_pretty_table

from .convertors import TABLE_ID, TABLE_VALUE, TABLE_ID_OR_VALUE

if sys.version_info[0] > 2:  # For Python 3
    # from abc import ABCMeta, abstractmethod
    def raw_input(prompt_msg):
        return input(prompt_msg)


def process(value, cleaners=None, convertor=None, validators=None, error_callback=print_error,
            convertor_error_fmt=DEFAULT_CONVERTOR_ERROR, validator_error_fmt=DEFAULT_VALIDATOR_ERROR):
    """
    runs a value through cleaning, conversion, and validation. This allows the same processing used
    in get_input to be performed on a value. For instance, the same processing used for getting 
    keyboard input can be applied to the value from a gui or web form input.

    :param value: the value to process
    :param cleaners: list of cleaners to apply to clean the value
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param error_callback: the function to call when an error occurs in conversion or validation
    :param convertor_error_fmt: format string fro convertor errors (defaults to DEFAULT_CONVERTOR_ERROR)
    :param validator_error_fmt: format string fro validator errors (defaults to DEFAULT_VALIDATOR_ERROR)

    :return: Return of tuple (valid, converted_value), if the values was cleaned, converted and validated successfully,
        valid is True and converted value is the converted and cleaned value. If not, valid is False, and value is None.
    """
    if cleaners:
        cleaned_response = compose(value, cleaners)
    else:
        cleaned_response = value

    try:
        if convertor:
            converted_response = convertor(cleaned_response, error_callback, convertor_error_fmt)
        else:
            converted_response = cleaned_response
    except ConvertorError:
        return (False, None)

    valid_response = in_all(converted_response, validators, error_callback, validator_error_fmt)

    if valid_response:
        return (True, converted_response)
    else:
        return (False, None)


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
    converted_response = None
    valid_response = None

    for k, v in options.items():
        if k == 'prompt':
            prompt_str = '%s' % v
        elif k == 'required':
            required = True if v else False
        elif k == 'default':
            default_val = str(v) if v else None
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
        default_str = ' (enter to leave blank)'
    elif default_val:
        default_str = ' (enter for: %s)' % default_string
    else:
        default_str = ''

    retries = 0
    input_str = '{}{}: '.format(prompt_str, default_str)
    print('')

    while (max_retries is None) or (retries < max_retries):
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

    if valid_response:
        return converted_response
    else:
        raise MaxRetriesError('Maximum retries exceeded')


def get_table_input(table=None, cleaners=None, convertor=None, validators=None, **options):
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
    input_value = TABLE_VALUE
    return_value = TABLE_VALUE
    show_table = True
    default_val = None
    sort_by_value = False
    valid_get_input_opts = ('value_error', 'prompt', 'required', 'default_str', 'hidden', 'retries', 'error_callback',
                            'convertor_error_fmt', 'validator_error_fmt')

    for k, v in options.items():
        if k == 'input_value':
            if v in {TABLE_ID, TABLE_VALUE, TABLE_ID_OR_VALUE}:
                input_value = v
            else:
                logging.warning('Warning: get_table_input received unknown value for input_value (%s)' % v)
        elif k == 'return_value':
            return_value = TABLE_VALUE if v else TABLE_ID
        elif k == 'show_table':
            show_table = v
        elif k == 'default':
            default_val = v
        elif k == 'sort_by_id':
            sort_by_value = v
        elif k not in valid_get_input_opts:
            logging.warning('Warning: get_table_input received unknown option (%s)' % k)

    # put together options to pass to get_input.
    convertor_options_to_keep = {'input_value', 'value_error'}
    get_input_options_to_skip = {'input_value', 'return_value', 'show_table', 'sort_by_id', 'value_error'}
    convertor_options = {k: v for k, v in options.items() if k in convertor_options_to_keep}
    get_input_options = {k: v for k, v in options.items() if k not in get_input_options_to_skip}

    if default_val and input_value == TABLE_ID:
        # Handle case where id inputted, but default value displayed
        get_input_options['default_str'] = str(default_val)
        for row in table:
            if row[TABLE_VALUE] == default_val or row[TABLE_ID] == default_val:
                get_input_options['default'] = row[TABLE_ID]
                break
        else:
            raise ValueError('default value not found in table.')

    if input_value == TABLE_ID_OR_VALUE:
        choices = tuple(item[TABLE_VALUE] for item in table) + tuple(item[TABLE_ID] for item in table)
    elif input_value == TABLE_VALUE:
        choices = tuple(item[TABLE_VALUE] for item in table)
    else:
        choices = tuple(item[TABLE_ID] for item in table)

    if validators and not callable(validators):
        table_validators = list(copy.deepcopy(validators)) + ChoiceValidator(choices=choices)
    else:
        table_validators = [ChoiceValidator(choices=choices)]

    if show_table:
        table_prompt = make_pretty_table(table, 'name', sort_by_value)
        print(table_prompt)

    convertor = TableConvertor(table, convertor, **convertor_options)
    returned_value = get_input(cleaners=cleaners, convertor=convertor, validators=table_validators, **get_input_options)

    # Make sure returned value is id or value as requested.
    if input_value == return_value:
        return returned_value
    else:
        for t in table:
            if input_value == TABLE_VALUE:
                if t[TABLE_VALUE] == returned_value:
                    return t[TABLE_ID]
            elif input_value == TABLE_ID:
                if t[TABLE_ID] == returned_value:
                    return t[TABLE_VALUE]
            else:  # input_value == TABLE_ID_OR_VALUE
                if t[TABLE_VALUE] == returned_value or t[TABLE_ID] == returned_value:
                    if return_value == TABLE_VALUE:
                        return t[TABLE_VALUE]
                    else:
                        return t[TABLE_ID]


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


def get_list(cleaners=(StripCleaner()), validators=None, **options):
    """
    Convenience function to get a list of values.

    :param cleaners: list of cleaners to apply to clean the value. Not needed in general.
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated list of values
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a list of values (separated by commas)'

    result = get_input(cleaners, convertor=ListConvertor(), validators=validators, **new_options)
    return result
