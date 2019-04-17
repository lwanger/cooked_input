"""
This is a simple database driven event list manager showing cooked_input menus, tables, and commands.

Len Wanger, 2019
"""

from datetime import date
import sqlite3
import cooked_input as ci

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
    if ci.get_yes_no(prompt='Delete all events from the database? ', default='no', commands=action_dict['commands']) == 'yes':
        action_dict['cursor'].execute('DELETE from events')
        action_dict['conn'].commit()
        action_dict['num_events'] = 0

def add_event_action(row, action_item):
    conn = action_dict['conn']
    cursor = action_dict['cursor']

    desc = ci.get_string(prompt="Event description? ", commands=commands_std)

    cursor.execute('SELECT name, desc, id FROM event_types ORDER BY name')
    tbl = ci.create_table(cursor, fields=["name", "desc"], field_names=["Name", "Desc"], add_item_to_item_data=True)
    event_type = tbl.get_table_choice(prompt='Event type? ', commands=commands_std)
    event_date = ci.get_date(prompt='Event date? ', default='today', commands=commands_std)

    action_dict['num_events'] = event_id = action_dict['num_events'] + 1
    sqlite_str = 'INSERT INTO events VALUES ({}, {}, "{}", "{}")'.format(event_id, event_date.toordinal(), desc, event_type.item_data['item']['id'])
    cursor.execute(sqlite_str)
    conn.commit()

def list_event_action(row, action_item):
    if action_dict['num_events'] == 0:
        print('\nno events\n')
        return

    cursor.execute('SELECT * FROM event_types')
    event_type_dict = {item['id']: item['name'] for item in cursor}

    cursor.execute('SELECT * FROM events ORDER BY date')
    items = []
    for event in cursor:
        date_str = date.fromordinal(event['date']).isoformat()
        type_str = event_type_dict[event['type']]
        items.append({'id': event['id'], 'date': date_str, 'desc': event['desc'], 'type': type_str})

    tbl = ci.create_table(items, fields=['id', 'date', 'desc', 'type'], field_names=['ID', 'Date', 'Desc', 'Type'], title='Events')
    print('\n')
    tbl.show_table()
    print('\n')

def database_submenu_action(row, action_item):
    menu_items = [ ci.TableItem('reset database (delete all events)', action=reset_db_action) ]
    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_RETURN, style=menu_style, action_dict=action_dict)
    menu.run()

def make_db():
    # Create an in memory sqlite database with tables for event types and events
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE event_types (id INTEGER PRIMARY_KEY, name text, desc text, recurrence int)''')
    cursor.execute("INSERT INTO event_types VALUES (1, 'birthday' ,'a birthday event', 2)")
    cursor.execute("INSERT INTO event_types VALUES (2, 'anniversary' ,'an anniversary event', 2)")
    cursor.execute("INSERT INTO event_types VALUES (3, 'meeting', 'a meeting event', 1)")

    cursor.execute('''CREATE TABLE events (id INTEGER PRIMARY_KEY, date int, desc text, type int)''')
    conn.commit()
    return conn, cursor

if __name__ == '__main__':
    conn, cursor = make_db()
    help_cmd = ci.GetInputCommand(help_cmd_action)
    cancel_cmd = ci.GetInputCommand(cancel_cmd_action)
    commands_std = { '/?': help_cmd, '/h': help_cmd, '/cancel': cancel_cmd }
    menu_style = ci.TableStyle(show_cols=False, show_border=False)
    action_dict = { 'conn': conn, 'cursor': cursor, 'commands': commands_std, 'num_events': 0 }

    menu_items = [
            ci.TableItem('Add an event', action=add_event_action),
            ci.TableItem('List events', action=list_event_action),
            ci.TableItem('Database submenu', action=database_submenu_action)
        ]
    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_EXIT, style=menu_style, action_dict=action_dict)
    menu.run()