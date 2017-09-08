
"""
Cooked input error callbacks

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

from __future__ import print_function

import sys
import logging

### cooked input custom exceptions
class MaxRetriesError(RuntimeError):
    # Exception raised when the maximum number of retries is exceeded.
    pass

class ValidationError(ValueError):
    # Exception raised when a value does not pass validation.
    pass


### Default error callback format strings
DEFAULT_CONVERTOR_ERROR = '"{value}" cannot be converted to {error_content}'
DEFAULT_VALIDATOR_ERROR = '"{value}" {error_content}'

### error callback routines

def print_error(fmt_str, value, error_content):
    """
    send errors to stdout. This displays errors on the screen.

    :param fmt_str: a Python format string for the error. Can use variables {value} and {error_content}.
    :param value:  the value the caused the error.
    :param error_content: additional information for the error

    :return: None
    """
    print(fmt_str.format(value=value, error_content=error_content), file=sys.stderr)


def silent_error(fmt_str, value, error_content):
    """
        Ignores errors, causing them to be silent

        :param fmt_str: a Python format string for the error. Can use variables {value} and {error_content}.
        :param value:  the value the caused the error.
        :param error_content: additional information for the error

        :return: None
    """
    pass


def log_error(fmt_str, value, error_content):
    """
        send errors to the log. See logging for details on using logs.

        :param fmt_str: a Python format string for the error. Can use variables {value} and {error_content}.
        :param value:  the value the caused the error.
        :param error_content: additional information for the error

        :return: None
    """
    logging.error(fmt_str.format(value=value, error_content=error_content))
