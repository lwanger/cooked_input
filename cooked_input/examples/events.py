"""
This is a simple event list manager showing cooked_input menus, tables, and commands.

Len Wanger, 2019
"""

from collections import namedtuple
import cooked_input as ci

EventType = namedtuple('EventType', 'id name desc')
Event = namedtuple('Event', 'id date desc type')

def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
    help_str = """
        Commands:
            /?, /help   Display this help message
            /cancel     Cancel the current operation
    """
    print(help_str)
    return ci.COMMAND_ACTION_NOP, None

def cancel_cmd_action(cmd_str, cmd_vars, cmd_dict):
    print('\nCommand cancelled...')
    return ci.COMMAND_ACTION_CANCEL, None

def reset_db_action(row, action_item):
    if ci.get_yes_no(prompt='Delete all events? ', default='no', commands=action_dict['commands']) == 'yes':
        action_dict['events'] = []

def add_event_action(row, action_item):
    events = action_dict['events']
    event_types = action_dict['event_types']

    event_desc = ci.get_string(prompt="Event description? ", commands=commands_std)

    tbl = ci.create_table(event_types, fields=["name", "desc"], field_names=["Name", "Desc"], add_item_to_item_data=True)
    event_type = tbl.get_table_choice(prompt='Event type? ', commands=commands_std)
    event_date = ci.get_date(prompt='Event date? ', default='today', commands=commands_std)
    event_type_id = event_type.item_data['item'].id
    events.append(Event(len(events)+1, event_date, event_desc, event_type_id))

def list_event_action(row, action_item):
    events = action_dict['events']
    event_types = action_dict['event_types']

    if len(events) == 0:
        print('\nno events\n')
        return

    event_type_dict = {item.id: item.name for item in event_types}

    items = []
    for event in events:
        date_str = event.date.isoformat()
        type_str = event_type_dict[event.type]
        items.append({'id': event.id, 'date': date_str, 'desc': event.desc, 'type': type_str})

    tbl = ci.create_table(items, fields=['id', 'date', 'desc', 'type'], field_names=['ID', 'Date', 'Desc', 'Type'], title='Events')
    print('\n')
    tbl.show_table()
    print('\n')

def database_submenu_action(row, action_item):
    menu_items = [ ci.TableItem('reset database (delete all events)', action=reset_db_action) ]
    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_RETURN, style=menu_style, action_dict=action_dict)
    menu.run()


if __name__ == '__main__':
    event_types = [EventType(1, 'birthday' ,'a birthday event'), EventType(2, 'anniversary' ,'an anniversary event'), EventType(3, 'meeting', 'a meeting event')]
    events = []
    help_cmd = ci.GetInputCommand(help_cmd_action)
    cancel_cmd = ci.GetInputCommand(cancel_cmd_action)
    commands_std = { '/?': help_cmd, '/h': help_cmd, '/cancel': cancel_cmd }
    menu_style = ci.TableStyle(show_cols=False, show_border=False)
    action_dict = { 'events': events, 'event_types': event_types, 'commands': commands_std }

    menu_items = [
            ci.TableItem('Add an event', action=add_event_action),
            ci.TableItem('List events', action=list_event_action),
            ci.TableItem('Database submenu', action=database_submenu_action)
        ]
    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_EXIT, style=menu_style, action_dict=action_dict)
    menu.run()