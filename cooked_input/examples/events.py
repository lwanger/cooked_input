"""
This is a simple event list manager showing cooked_input menus, tables, and commands.

Len Wanger, 2019
"""

from collections import namedtuple
from typing import Any

import cooked_input as ci

EventType = namedtuple('EventType', 'id name desc')
Event = namedtuple('Event', 'id date desc type')

event_types = [
    EventType(1, 'birthday' ,'a birthday event'),
    EventType(2, 'anniversary' ,'an anniversary event'),
    EventType(3, 'meeting', 'a meeting event')
]
events = []

def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
    help_str = """
        Commands:
            /?, /help   Display this help message
            /cancel     Cancel the current operation
    """
    print(help_str)
    return ci.CommandResponse(ci.COMMAND_ACTION_NOP, None)

def cancel_cmd_action(cmd_str, cmd_vars, cmd_dict):
    if ci.get_yes_no(prompt='Are you sure you want to cancel?', default='no') == 'yes':
        print('\nCommand cancelled...')
        return ci.CommandResponse(ci.COMMAND_ACTION_CANCEL, None)
    else:
        return ci.CommandResponse(ci.COMMAND_ACTION_NOP, None)

help_cmd = ci.GetInputCommand(help_cmd_action)
cancel_cmd = ci.GetInputCommand(cancel_cmd_action)
app_cmds = {'/?': help_cmd, '/h': help_cmd, '/cancel': cancel_cmd}


# Each action receives the table's action_dict as its second argument. Reading the module
# global instead worked only because __main__ happened to create one -- importing this module
# and running a menu would have raised NameError.
def reset_db_action(row, action_item: dict[str, Any]):
    cmds = action_item['commands']
    if ci.get_yes_no(prompt='Delete all events? ', default='no', commands=cmds) == 'yes':
        action_item['events'] = []

def add_event_action(row, action_item: dict[str, Any]):
    events = action_item['events']
    event_types = action_item['event_types']
    cmds = action_item['commands']
    desc = ci.get_string(prompt="Event description? ", commands=cmds)
    tbl = ci.create_table(event_types, ["name", "desc"], ["Name", "Desc"], add_item_to_item_data=True)
    event_type = tbl.get_table_choice(prompt='Type? ', commands=cmds)
    date = ci.get_date(prompt='Date? ', default='today', commands=cmds)
    type_id = event_type.item_data['item'].id
    events.append(Event(len(events)+1, date, desc, type_id))

def list_event_action(row, action_item: dict[str, Any]):
    events = action_item['events']
    event_types = action_item['event_types']

    if len(events) == 0:
        print('\nno events\n')
        return

    et_dict = {item.id: item.name for item in event_types}
    items = []
    for e in events:
        date = e.date.strftime('%x')
        etype = et_dict[e.type]
        items.append({'id': e.id, 'date': date, 'desc': e.desc, 'type': etype})

    fields = ['date', 'desc', 'type']
    field_names = ['Date', 'Desc', 'Type']
    tbl = ci.create_table(items, fields, field_names, title='Events')
    print('\n')
    tbl.show_table()
    print('\n')

def db_submenu_action(row, action_item: dict[str, Any]):
    # Was action_item['menu_style'], a key the dict below has never had -- choosing this
    # menu item raised KeyError before it could draw the sub-menu.
    style = action_item['style']
    items = [ ci.TableItem('Delete all events', action=reset_db_action) ]
    menu = ci.Table(rows=items, add_exit=ci.TABLE_ADD_RETURN, style=style, action_dict=action_item)
    menu.run()

if __name__ == '__main__':
    style = ci.TableStyle(show_cols=False, show_border=False)
    action_dict: dict[str, Any] = { 'events': events, 'event_types': event_types, 'commands': app_cmds, 'style': style }

    items = [
            ci.TableItem('Add an event', action=add_event_action),
            ci.TableItem('List events', action=list_event_action),
            ci.TableItem('Database submenu', action=db_submenu_action)
        ]
    menu = ci.Table(rows=items, add_exit=ci.TABLE_ADD_EXIT, style=style, action_dict=action_dict)
    menu.run()