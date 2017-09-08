
"""
pytest tests for cooked_input -- get_input_table tests


Len Wanger, 2017
"""

from io import StringIO
from cooked_input import get_table_input, TABLE_ID, TABLE_VALUE, TABLE_ID_OR_VALUE
from cooked_input import TableConvertor, BooleanConvertor
from cooked_input import StripCleaner
from .utils import redirect_stdin


class TestTables(object):

    table = [(1, 'red'), (2, 'blue'), (4, 'green'), (6, 'yellow')]
    cur_val = 'red'

    def test_base_class(self):
        tc = TableConvertor(self.table, None)
        print(tc)


    def test_get_table_input(self):
        input_str = u"""
        
            10
            green
            2
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_table_input(table=self.table, cleaners=StripCleaner(), convertor=None, validators=None,
                                input_value=TABLE_ID, return_value=TABLE_ID, show_table=True,
                                prompt='Enter the id of the color you want', value_error='a valid color id')
            print(result)
            assert(result==2)

        with redirect_stdin(StringIO(input_str)):
            result = get_table_input(table=self.table, cleaners=StripCleaner(), convertor=None, validators=None, input_value=TABLE_ID, return_value=TABLE_VALUE, show_table=True,
                                 default=self.cur_val, prompt='Enter the id of the color you want')
            print(result)
            assert(result=='red')

        with redirect_stdin(StringIO(input_str)):
            result = get_table_input(table=self.table, cleaners=StripCleaner(), convertor=BooleanConvertor(), validators=None, input_value=TABLE_ID, return_value=TABLE_ID, show_table=True,
                                 default=self.cur_val, prompt='Enter the id of the color you want')
            print(result)
            assert(result==True)


        with redirect_stdin(StringIO(input_str)):
            result =  get_table_input(table=self.table, cleaners=StripCleaner(), convertor=None, validators=None, input_value=TABLE_VALUE, return_value=TABLE_VALUE, show_table=True,
                                 prompt='Enter the name of color you want')
            print(result)
            assert(result=='green')

        with redirect_stdin(StringIO(input_str)):
            result =  get_table_input(table=self.table, cleaners=StripCleaner(), convertor=None, validators=None, input_value=TABLE_ID_OR_VALUE, return_value=TABLE_VALUE, show_table=True,
                                 prompt='Enter the name or id of the color you want')
            print(result)
            assert(result=='green')

        input_str = u"""
            10
            4
            2
            """

        with redirect_stdin(StringIO(input_str)):
            result =  get_table_input(table=self.table, cleaners=StripCleaner(), convertor=None, validators=None, input_value=TABLE_ID_OR_VALUE, return_value=TABLE_ID, show_table=True)
            print(result)
            assert(result==4)