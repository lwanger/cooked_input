# test create_table:
from collections import namedtuple
from cooked_input import create_table, TableStyle, TABLE_RETURN_ROW, TABLE_RETURN_TABLE_ITEM, RULE_FRAME, RULE_ALL

def test_create_table(items, fields, field_names, gen_tags, tag_str, item_data=None, add_item_to_item_data=False,
        add_exit=False, prompt=None, style=None, default_choice=None, default_action=TABLE_RETURN_ROW):

    tbl = create_table(items, fields, field_names=field_names, gen_tags=gen_tags, tag_str=tag_str,
                       item_data=item_data,
                       add_item_to_item_data=add_item_to_item_data, add_exit=add_exit, style=style,
                       default_choice=default_choice,
                       default_action=default_action, prompt=prompt)
    print()
    recipe_ti = tbl.get_table_choice(commands=None)
    print(recipe_ti)


prompt = None
item_data = None
add_exit = False
aitid = False  # Add item data to item data
default_action = TABLE_RETURN_ROW
default_choice=None
table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)

# test different type of items lists...
if True:  # single item list, generate tags
    print('\nTest list of single items - autogen tags\n')
    items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
    fields = 'name'.split()
    field_names = 'Name'.split()
    gen_tags = True
    tag_str = ''
    prompt = 'Choose a printer'
    test_create_table(items, fields, field_names, gen_tags, tag_str, prompt=prompt, style=table_style)


if True:  # single item list
    print('\nTest list of single items (no autogen tags)\n')
    items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
    fields = 'name'.split()
    field_names = 'Name'.split()
    gen_tags = False
    tag_str = 'Printer'
    add_exit = True
    test_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=table_style)

if True:  # multi item list
    print('\nTest list of multiple items (no autogen tags)\n')
    items = [["Beast", "IO-PROD", "Model One G2"], ["Ford2", "Dearborn", "Model One G2.1"],
             ["Seth", "IO-PROD", "Cell"]]
    fields = 'name location model'.split()
    field_names = 'Name Location IO_Model'.split()
    gen_tags = False
    tag_str = None
    test_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)

if True:  # Dictionary of dictionaries
    print('\nTest list of dictionary of dictionaries (no autogen tags)\n')
    items = {1: {"name": "Beast", "location": "IO-PROD", "model": "Model One G2"},
             2: {"name": "Ford2", "location": "Dearborn", "model": "Model One G2.1"},
             3: {"name": "Seth", "location": "IO-PROD", "model": "Cell"}}
    fields = 'name location model'.split()
    field_names = 'Name Location IO_Model'.split()
    gen_tags = False
    tag_str = "Printer"
    test_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)

if True:  # Dictionary of lists
    print('\nTest list of dictionary of lists (autogen tags)\n')

    items = {1: ["Beast", "IO-PROD", "Model One G2"], 2: ["Ford2", "Dearborn", "Model One G2.1"],
             3: ["Seth", "IO-PROD", "Cell"]}
    fields = 'name location model'.split()
    field_names = 'Name Location IO_Model'.split()
    gen_tags = True
    tag_str = "Printer"
    test_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)

if True:  # Class -- make a table of TableStyles (convenient class to use)
    print('\nTest list of class instances (autogen tags)\n')

    items = [
        TableStyle(True, True,RULE_FRAME, RULE_FRAME),
        TableStyle(True, False, RULE_FRAME, RULE_FRAME),
        TableStyle(False, True, RULE_ALL, RULE_FRAME),
        TableStyle(False, False, RULE_FRAME, RULE_ALL),
    ]
    fields = 'show_cols hrules vrules'.split()  # no show_border on purpose
    field_names = 'Show_Cols H-Rules V-Rules'.split()
    gen_tags = True
    tag_str = "Table Style"
    test_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)

if True:
    print('\nTest list of named tuples (autogen tags)\n')

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
    item_data = {'foo': 'I am foo', 'bar': [1, 2, 3]}
    aitid = True
    default_action = TABLE_RETURN_TABLE_ITEM
    test_create_table(items, fields, field_names, gen_tags, tag_str, item_data=None, add_item_to_item_data=aitid,
                      style=table_style, default_action=default_action)


