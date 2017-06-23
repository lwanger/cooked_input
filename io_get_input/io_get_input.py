
"""
get_input module to get values from the command line.

document usage.
point to examples
talk about convertors, cleaners, and validators

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
import copy
import logging
import getpass
import prettytable

# relative import needed to run, but sphinx need non-relative. 
from .validators import InChoicesValidator, in_all
from .convertors import TableConvertor
# from validators import InChoicesValidator
# from convertors import TableConvertor


TABLE_ID = 0
TABLE_VALUE = 1
TABLE_ID_OR_VALUE = -1


if sys.version_info[0] > 2: # For Python 3
    # from abc import ABCMeta, abstractmethod
    def raw_input(prompt_msg):
        return input(prompt_msg)


def compose(value, funcs):
    # compose functions and return the result: compose(value, [f1,f2,f3]) = f3(f2(f1(value)))
    result = None
    if callable(funcs):
        result = funcs(value)
    else:
        for func in funcs:
            if not result:
                result = func(value)
            else:
                result = func(result)
    return result


def process_value(value, cleaners, convertor, validators):
    """
    runs a value through cleaning, conversion, and validation. This allows the same processing used in get_input to be
    performed on a value. For instance, the same processing used for getting keyboard input can be applied to the value
    from a web form input.

    :param value: the value to process
    :param cleaners: list of cleaners to apply to clean the value
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value
    :return: a tuple (valid_response, converted_response). valid_response is True is the validation passed.
    """
    if cleaners:
        cleaned_response = compose(value, cleaners)
    else:
        cleaned_response = value

    try:
        if convertor:
            converted_response = convertor(cleaned_response)
        else:
            converted_response = cleaned_response
    except ValueError:
        print('value should be %s.' % convertor.value_error_str)
        return False, None

    valid_response = in_all(converted_response, validators)
    return valid_response, converted_response


def make_pretty_table(rows, second_col_name='name', sort_by_second_col=True):
    """
    Take a list of tuples [(id, value), ...] and return a prettytable

    :param rows: a list of tuples for the table rows. Each tuple is: (id, value).
    :param second_col_name: the name to use for the header on the second column.
    :param sort_by_second_col: sort by the second column if True, otherwise leave in order from rows.
    :return: a prettytable for the table.
    """
    x = prettytable.PrettyTable(['id', second_col_name])

    for row in rows:
        x.add_row([row[0], row[1]])

    x.align[second_col_name] = 'l'  # left align
    x.sortby = second_col_name if sort_by_second_col else 'id'
    return x


def get_input(cleaners=None, convertor=None, validators=None, **options):
    """
    Get input from the command line and return a validated response.

    get_input prompts the user for an input. The input is then cleaned, converted, and validated, 
    and the validated response is returned.

    <stay tuned for more...>

    Options:

        prompt: the string to use for the prompt. For example prompt="Enter your name"

        blank_ok: True if a blank response is OK.

        default: the default value to use if a blank string is entered. This takes precedence over 
            blank_ok (i.e.  a blank response will return the default value.)

        default_str: the string to use for the default value. In general just set the default option. 
            This is used by get_from_table to display a value but return a table id.

        hidden: the input typed should not be displayed. This is useful for entering passwords.

        retries: the maximum number of attempts to allow before raising a RuntimeError.

    :param cleaners: list of cleaners to apply to clean the value
    :param convertor: the convertor to apply to the cleaned value
    :param validators: list of validators to apply to validate the cleaned and converted value
    :param options:  see above
    :return: the cleaned, converted, validated input. Returns None if a valid input was not entered within max retries.
    """

    prompt_str = ''
    blank_ok = False
    default_val = None
    default_string = None
    hidden = False
    max_retries = None

    for k, v in options.items():
        if k=='prompt':
            prompt_str = '%s' % v
        elif k=='blank_ok':
            blank_ok = True if v else False
        elif k == 'default':
            default_val = str(v) if v else None
        elif k == 'default_str':    # for get_from_table may want to display value but return id.
            default_string = v
        elif k == 'hidden':
            hidden = v
        elif k == 'retries':
            max_retries = v
        else:
            logging.warning('Warning: get_input received unknown option (%s)' % k)

    if default_val is not None and not default_string:
        default_string = str(default_val)

    if blank_ok and default_val is not None:
        # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
        # logging.warning('Warning: both blank_ok and a default value specified. Blank inputs will use default value.')
        blank_ok = False

    if blank_ok and not default_val:
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

        if blank_ok and not response:
            return None
        elif default_val and not response:
            valid_response, converted_response = process_value(default_val, cleaners, convertor, validators)
            if valid_response:
                return converted_response
            else:
                raise ValueError('default did not pass validation.')
        elif response:
            valid_response, converted_response  = process_value(response, cleaners, convertor, validators)

            if valid_response:
                break
            else:
                retries += 1
                # print('TODO: get validation error messages')
                continue

    if valid_response:
        return converted_response
    else:
        raise RuntimeError('Maximum retries exceeded')


def get_table_input(table=None, cleaners=None, convertor=None, validators=None, **options):
    """
    Get input value from a table of values. Allow to type in and return either the id or the value 
    for the choice. Useful for entering values from database tables.

    options:

        input_value: TABLE_VALUE (or True) to input the value from the table row, TABLE_ID (or False) 
            to enter the id. TABLE_ID_OR_VALUE  allows entering either and will give the preference
            to entering the value.

        return_value: TABLE_VALUE (or True) to return the value from the table row, TABLE_ID (or
            False) to return the id.  show_table: will print the table before asking for the prompt 
            before asking for the input.

        sort_by_value: whether to sort the table rows by value (True) or id (False). Defaults to sort by id.
        default: the default value to use.

    :param table: list of tuples, with each tuple being: (id, value) for the items in the table.
    :param cleaners: list of cleaners to apply to the inputted value.
    :param convertor: the convertor to apply to the cleaned input value.
    :param validators: list of validators to apply to the cleaned, converted input value.
    :param options: see above
    :return: the cleaned, converted, validated input value. This is an id or value from the table depending on input_value.
    """
    input_value = TABLE_VALUE
    return_value = TABLE_VALUE
    show_table = True
    default_val = None
    sort_by_value = False

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
        elif k not in ('value_error', 'prompt', 'blank_ok' ):
            logging.warning('Warning: get_table_input received unknown option (%s)' % k)

    # put together options to pass to get_input.
    convertor_options_to_keep = {'input_value', 'value_error'}
    get_input_options_to_skip = {'input_value', 'return_value', 'show_table', 'sort_by_id', 'value_error'}
    convertor_options = {k: v for k, v in options.items() if k in convertor_options_to_keep}
    get_input_options = {k: v for k, v in options.items() if k not in get_input_options_to_skip}

    if default_val and input_value==TABLE_ID:
        # Handle case where id inputed, but default value displayed
        get_input_options['default_str'] = str(default_val)
        for row in table:
            if row[TABLE_VALUE] == default_val or  row[TABLE_ID] == default_val:
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
        table_validators = list(copy.deepcopy(validators)) + InChoicesValidator(choices=choices)
    else:
        table_validators = [InChoicesValidator(choices=choices)]

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
            else: # input_value == TABLE_ID_OR_VALUE
                if t[TABLE_VALUE] == returned_value or t[TABLE_ID] == returned_value:
                    if return_value == TABLE_VALUE:
                        return t[TABLE_VALUE]
                    else:
                        return t[TABLE_ID]


def validate(value, validators=None):
    """
    Run validators on a value.

    :param value: the value to validate.
    :param validators: list of validators to run on the value.
    :return: True if the input passed validation, else False
    """
    return compose(value, validators)


if __name__ == '__main__':
    pass
    # if False:
    #     length_val = InLengthValidator(5, 10)
    #     exact_len_val = ExactLengthValidator(7)
    #     between_val = InRangeValidator(10, 20)
    #     exact_val_val = ExactValueValidator(11)
    #
    #     choice_list = [5, 10, 15]
    #     in_choices = InChoicesValidator(choice_list)
    #
    #     choice_str_list = ['1234567', 'abcdefg', 'foobars']
    #     in_str_choices = InChoicesValidator(choice_str_list)
    #
    #     print('length_val = %r' % length_val )
    #     print('exact_len_val = %r' % exact_len_val )
    #     print('between_val = %r' % between_val )
    #
    #     print('length_val(\'does not pass\')=%r' % length_val('does not pass'))
    #     print('length_val(\'passes\')=%r' % length_val('passes'))
    #     print('exact_len_val(\'not passess\')=%r' % exact_len_val('not passess'))
    #     print('exact_len_val(\'passess\')=%r' % exact_len_val('passess'))
    #     print('between_val(5)=%r' % between_val(5))
    #     print('between_val(11)=%r' % between_val(11))
    #     print('exact_val_val(11)=%r' % exact_val_val(11))
    #
    #     # throw a TypeError exception
    #     try:
    #         print('length_val(11)=%r' % length_val(11))
    #     except:
    #         print('TypeError as expected from: length_val(11)=%r' % length_val)
    #
    #     # try choices
    #     print('in_choices(\'foo\', %r)' % choice_list, in_choices('foo'))
    #     print('in_choices(10, %r)' % choice_list, in_choices(10))
    #
    #     # Try any and all:
    #     print('in_any(11, [%r, %r])' % (exact_val_val, between_val), in_any(11, [exact_val_val, between_val]))
    #     print('in_all(11, [%r, %r, %r])' % (exact_val_val, between_val, in_choices), in_all(11, [exact_val_val, between_val, in_choices]))
    #     print('in_all(10, [%r, %r])' % (between_val, in_choices), in_all(10, [between_val, in_choices]))
    #
    #     # choices has a mutable list so can be changed dynamically
    #     choice_list.remove(10)
    #     print('not in_choices(10, %r)' % choice_list, not in_choices(10))
    #
    #     # Test cleaners and compose
    #     lower_cleaner = LowerCleaner()
    #     strip_cleaner = StripCleaner(lstrip=True, rstrip=True)
    #     unclean_str = 'Foo \t'
    #     funcs = [lower_cleaner, strip_cleaner]
    #     result = compose(unclean_str, funcs)
    #     print('compose(\'%s\', %r)=%s' % (unclean_str, funcs, result))
    #
    #     # test validate
    #     print(validate('foo', validators=[ExactLengthValidator(3)]))
    #     print(validate(13.3, validators=[ExactValueValidator(13.3)]))
    #     print(validate(13.3, validators=[InRangeValidator(13.1, 13.4)]))
    #     print('expect False: %r' % validate(13.3, validators=[InRangeValidator(12.1, 12.4)]))
    #
    #     # test get_input
    #     result = get_input(cleaners=[lower_cleaner, strip_cleaner], convertor=None, validators=[])
    #     print('string input result=%r' % (result))
    #
    #     options = {'prompt': 'give me an integer between 10 and 20', 'default': '15', 'blank_ok': True}
    #     prompt_str = 'give me an integer between 10 and 20'
    #     result = get_input(cleaners=None, convertor=IntConvertor(), validators=[between_val], prompt=prompt_str, default=15, blank_ok=True)
    #     print('int input result=%r' % (result))
    #
    #     result = get_input(cleaners=[LowerCleaner()], convertor=None, validators=[in_str_choices], prompt='give me a string', retries=2)
    #     print('str in choice input result=%r' % (result))
    #
    #     # Test getting a password
    #     password_val = PasswordValidator(disallowed='[]', min_length=5, max_length=15, min_lower=2, min_upper=2, min_digits=1, min_puncts=2)
    #     result = get_input(cleaners=None, convertor=None, validators=[password_val], prompt='password', blank_ok=False, hidden=True)
    #     print('password result=%r' % (result))
    #
    # # test get_table_input:
    # traveler_data = {}
    # table = [(1, 'ben'), (2, 'darren'), (4, 'elan'), (6, 'schlomo')]
    # cur_val = 'ben'
    #
    # ir_list = [(TABLE_ID, 'id'), (TABLE_VALUE, 'value'), (TABLE_ID_OR_VALUE, 'id or value')]
    # for ir in ir_list:
    #     print('get_table by %s' % ir[1])
    #     technician = get_table_input(table=table, cleaners=None, convertor=None, validators=None, input_value=ir[0], return_value=TABLE_VALUE, show_table=True,
    #                                  default=cur_val, prompt='Enter the %s of the technician to use'%ir[1], value_error='not a valid technician %s'%ir[1])
    #     print('technician=%s' % (technician))
