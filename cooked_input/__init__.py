# -*- coding: utf-8 -*-

from .get_input import GetInput, get_input, process_value
from .get_input import get_string, get_int, get_float, get_boolean, get_date, get_yes_no, get_list
from .get_input import GetInputInterrupt
from .get_input import GetInputCommand, CommandResponse, COMMAND_ACTION_USE_VALUE, COMMAND_ACTION_CANCEL, COMMAND_ACTION_NOP
from .get_input import cancel_cmd_action

from .error_callbacks import MaxRetriesError, ConvertorError, ValidationError
from .error_callbacks import print_error, log_error, silent_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR

from .cleaners import Cleaner, CapitalizationCleaner, LOWER_CAP_STYLE, UPPER_CAP_STYLE, FIRST_WORD_CAP_STYLE, ALL_WORDS_CAP_STYLE
from .cleaners import StripCleaner, RemoveCleaner, ReplaceCleaner, ChoiceCleaner, RegexCleaner

from .convertors import Convertor, IntConvertor, FloatConvertor, BooleanConvertor
from .convertors import ListConvertor, DateConvertor, YesNoConvertor, ChoiceConvertor

from .validators import Validator, LengthValidator, EqualToValidator, RangeValidator
from .validators import AnyOfValidator, NoneOfValidator, ChoiceValidator, RegexValidator, PasswordValidator
from .validators import IsFileValidator, ListValidator, SimpleValidator
from .validators import in_all, in_any, not_in, validate

from .input_utils import put_in_a_list, isstring

from .version import __version__
