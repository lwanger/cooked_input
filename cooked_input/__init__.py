# -*- coding: utf-8 -*-

from .get_input import get_input, get_table_input, process
from .get_input import get_string, get_int, get_float, get_boolean, get_date, get_yes_no, get_list
from .get_menu import get_menu, Menu, MenuItem
from .get_menu import MENU_ACTION_EXIT, MENU_ACTION_RETURN, MENU_DEFAULT_ACTION, MENU_ADD_EXIT, MENU_ADD_RETURN
from .error_callbacks import MaxRetriesError, ConvertorError, ValidationError
from .error_callbacks import print_error, log_error, silent_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .convertors import TABLE_ID, TABLE_VALUE, TABLE_ID_OR_VALUE
from .convertors import Convertor, IntConvertor, FloatConvertor, BooleanConvertor
from .convertors import ListConvertor, DateConvertor, YesNoConvertor, TableConvertor, ChoiceIndexConvertor
from .validators import Validator, LengthValidator, EqualToValidator, RangeValidator
from .validators import AnyOfValidator, NoneOfValidator, ChoiceValidator, RegexValidator, PasswordValidator
from .validators import ListValidator, SimpleValidator
from .validators import in_all, in_any, not_in, validate
from .cleaners import Cleaner, CapitalizationCleaner, LOWER_CAP_STYLE, UPPER_CAP_STYLE, FIRST_WORD_CAP_STYLE, ALL_WORDS_CAP_STYLE
from .cleaners import StripCleaner, RemoveCleaner, ReplaceCleaner, ChoiceCleaner, RegexCleaner
from .input_utils import make_pretty_table

__version__ = '0.3.0'
