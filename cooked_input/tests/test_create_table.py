# test create_table:


from collections import namedtuple
from cooked_input import create_table, create_rows, Table, TableStyle
from cooked_input import TABLE_RETURN_ROW, TABLE_RETURN_TABLE_ITEM, RULE_FRAME, RULE_ALL


class Person(object):
    def __init__(self, first, last, age, shoe_size):
        self.first = first
        self.last = last
        self.age = age
        self.shoe_size = shoe_size


def use_create_table(items, fields, field_names, gen_tags, tag_str, item_data=None, add_item_to_item_data=False,
                     add_exit=False, prompt=None, style=None, default_choice=None, default_action=TABLE_RETURN_ROW):

    # prompt = None
    tbl = create_table(items, fields, field_names=field_names, gen_tags=gen_tags, tag_str=tag_str,
                       item_data=item_data,
                       add_item_to_item_data=add_item_to_item_data, add_exit=add_exit, style=style,
                       default_choice=default_choice,
                       default_action=default_action, prompt=prompt)
    return tbl.get_table_choice(commands=None)


class TestTables(object):
    def test_show_table_renders_headers_and_every_row(self, capsys):
        people = [
            Person('John', 'Cleese', 78, 14),
            Person('Terry', 'Gilliam', 77, 10),
            Person('Eric', 'Idle', 75, 12),
        ]

        rows = create_rows(people, ['last', 'first', 'shoe_size'])
        Table(rows, ['First', 'Shoe Size'], tag_str='Last').show_table()

        rendered = capsys.readouterr().out
        # tag_str supplies the first column heading, col_names the rest.
        for heading in ('Last', 'First', 'Shoe Size'):
            assert heading in rendered
        for surname in ('Cleese', 'Gilliam', 'Idle'):
            assert surname in rendered
        for shoe_size in ('14', '10', '12'):
            assert shoe_size in rendered

    def test_get_table_choice(self, fake_input):
        input_str = '1'

        items = {
            1: {"episode": 1, "name": "Whither Canada?", "date": "5 October, 1969", "season": 1},
            2: {"episode": 4, "name": "Owl Stretching Time", "date": "26 October, 1969", "season": 1},
            3: {"episode": 15, "name": "The Spanish Inquisition", "date": "22 September, 1970", "season": 2},
            4: {"episode": 35, "name": "The Nude Organist", "date": "14 December, 1972", "season": 2}
        }

        fields = 'episode name date'.split()
        field_names = 'Episode Name Date'.split()
        tbl = create_table(items, fields, field_names, add_item_to_item_data=True,
                           title='And Now For Something Completely different')

        fake_input(input_str)
        choice = tbl.get_table_choice()
        item = choice.item_data["item"]
        assert (item['name'] == 'Whither Canada?')

    def test_single_col_table_autogen_tags_chosen_by_tag(self, fake_input, framed_style):
        # single item list, generate tags
        input_str = '2'

        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        gen_tags = True
        tag_str = ''
        prompt = 'Choose a printer'

        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, prompt=prompt, style=framed_style)
        assert (result == [2, 'Deuce'])


    def test_single_col_table_no_autogen_chosen_by_value(self, fake_input, framed_style):
        # single item list
        input_str = 'Beast'

        prompt = None
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        gen_tags = False
        tag_str = 'Printer'
        add_exit = True

        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=framed_style)

        assert (result == ['Beast'])


    def test_single_col_table_exit_row_yields_no_selection(self, fake_input, framed_style):
        # Regression guard for #47: this used to hand back the TableItem for the exit row.
        # Choosing Exit means no row was chosen, which is what Table.run has always
        # assumed and what get_table_choice documents for a blank entry.
        input_str = 'exit'

        prompt = None
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        gen_tags = False
        tag_str = 'Printer'
        add_exit = True

        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=framed_style)

        assert result is None


    def test_single_item_table(self, fake_input, framed_style):
        input_str = 'Beast'

        prompt = None
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        gen_tags = False
        tag_str = 'Printer'
        add_exit = True
        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=framed_style)

        assert (result == ['Beast'])


    def test_multi_item_list(self, fake_input, framed_style):
        input_str = 'Ford2'

        items = [["Beast", "IO-PROD", "Model One G2"], ["Ford2", "Dearborn", "Model One G2.1"],
                 ["Seth", "IO-PROD", "Cell"]]
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        gen_tags = False
        tag_str = None
        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=framed_style)
        assert (result == ["Ford2", "Dearborn", "Model One G2.1"] )

    def test_dict_of_dicts(self, fake_input, framed_style):
        input_str = 'Seth'

        items = {1: {"name": "Beast", "location": "IO-PROD", "model": "Model One G2"},
                 2: {"name": "Ford2", "location": "Dearborn", "model": "Model One G2.1"},
                 3: {"name": "Seth", "location": "IO-PROD", "model": "Cell"}}
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        gen_tags = False
        tag_str = "Printer"
        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=framed_style)
        assert (result == ["Seth", "IO-PROD", "Cell"] )


    def test_dict_of_lists(self, fake_input, framed_style):
        input_str = '3'


        items = {1: ["Beast", "IO-PROD", "Model One G2"], 2: ["Ford2", "Dearborn", "Model One G2.1"],
                 3: ["Seth", "IO-PROD", "Cell"]}
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        gen_tags = True
        tag_str = "Printer"
        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=framed_style)
        assert (result == [3, "Seth", "IO-PROD", "Cell"] )


    def test_table_of_tablestyles(self, fake_input, framed_style):
        input_str = '3'


        items = [
            TableStyle(True, True, RULE_FRAME, RULE_FRAME),
            TableStyle(True, False, RULE_FRAME, RULE_FRAME),
            TableStyle(False, True, RULE_ALL, RULE_FRAME),
            TableStyle(False, False, RULE_FRAME, RULE_ALL),
        ]
        fields = 'show_cols hrules vrules'.split()  # no show_border on purpose
        field_names = 'Show_Cols H-Rules V-Rules'.split()
        gen_tags = True
        tag_str = "Table Style"
        fake_input(input_str)
        result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=framed_style)
        assert (result == [3, False, 1, 0] )


    def test_named_tuple(self, fake_input, framed_style):
        input_str = '3'

        MyTuple = namedtuple("MyTuple", "name location model other")
        items = [
            MyTuple("Beast", "IO-PROD", "Model One G2", "Other stuff"),
            MyTuple("Ford2", "Dearborn", "Model One G2.1", "Other stuff"),
            MyTuple("Seth", "IO-PROD", "Cell", "Seth Other stuff"),
        ]
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        gen_tags = True
        tag_str = None
        aitid = True
        default_action = TABLE_RETURN_TABLE_ITEM
        fake_input(input_str)
        ti = use_create_table(items, fields, field_names, gen_tags, tag_str, item_data=None,
                          add_item_to_item_data=aitid, style=framed_style, default_action=default_action)

        assert (ti.item_data['item'].name == 'Seth')
        assert (ti.tag == 3)
