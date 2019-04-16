"""
Start of a DB/table example

Do example with event list manager

DB
Menu, submenu
Table
To gui

TODO:
    - tighten up
    - document
    - get more sensible command than /dow... add a filter to list?
    - add to GUI
"""

from datetime import date
import sqlite3
import cooked_input as ci

def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
    help_str = """
        Commands:
            /?, /help   Display this help message
            /cancel     Cancel the current operation
            /dow        Get the day of the week for a date
    """
    print(help_str)
    return ci.COMMAND_ACTION_NOP, None

def cancel_cmd_action(cmd_str, cmd_vars, cmd_dict):
    print('\nCommand cancelled...')
    return ci.COMMAND_ACTION_CANCEL, None

def day_of_week_cmd_action(cmd_str, cmd_vars, cmd_dict):
    if len(cmd_vars) > 0:
        date_str = cmd_vars
        valid, date = ci.process_value(date_str, convertor=ci.DateConvertor())
        if valid is False:
            return ci.COMMAND_ACTION_CANCEL, None
    else:
        date = ci.get_date(prompt='Date to get day of week from: ')
    return ci.COMMAND_ACTION_USE_VALUE, date.strftime('%A')

def reset_db_action(row, action_item):
    if ci.get_yes_no(prompt='Delete all events from the database? ', default='no') == 'yes':
        action_dict['cursor'].execute('DELETE from events')
        action_dict['conn'].commit()
        action_dict['num_events'] = 0


def add_event_action(row, action_item):
    conn = action_dict['conn']
    conn.row_factory = sqlite3.Row
    cursor = action_dict['cursor']

    desc = ci.get_string(prompt="Event description? ", commands=commands_std)

    cursor.execute('SELECT name, desc FROM event_types ORDER BY name')
    fields = ["name", "desc"]
    field_names = ["Name", "Desc"]
    tbl = ci.create_table(cursor, fields, field_names, gen_tags=False)
    event_type = tbl.get_table_choice(prompt='Event type? ', commands=commands_std)
    event_date = ci.get_date(prompt='Event date? ', default='today', commands=commands_std)

    action_dict['num_events'] = event_id = action_dict['num_events'] + 1
    sql_str = 'INSERT INTO events VALUES ({}, {}, "{}", "{}")'.format(event_id, event_date.toordinal(), desc, event_type.values[0])
    cursor.execute(sql_str)
    conn.commit()

def list_event_action(row, action_item):
    if action_dict['num_events'] == 0:
        print('\nno events\n')
        return

    cursor.execute('SELECT * FROM event_recurrences')
    event_recurrence_dict = {item['id']: (item['name'], item['desc']) for item in cursor}
    cursor.execute('SELECT * FROM event_types')
    event_type_dict = {item['id']: (item['name'], item['desc'], event_recurrence_dict[item['recurrence']][0]) for item in cursor}

    cursor.execute('SELECT * FROM events ORDER BY date')
    fields = ['id', 'date', 'desc', 'type']
    field_names = ['ID', 'Date', 'Desc', 'Type']
    items = []
    for event in cursor:
        # date_str = datetime.fromordinal(event['date']).strftime('%x')
        date_str = date.fromordinal(event['date']).isoformat()
        type_str = event_type_dict[event['id']][0]
        event_entry = {'id': event['id'], 'date': date_str, 'desc': event['desc'], 'type': type_str}
        items.append(event_entry)

    tbl = ci.create_table(items, fields, field_names, title='Events')
    print('\n')
    tbl.show_table()
    print('\n')


def database_submenu_action(row, action_item):
    menu_items = [
        ci.TableItem(col_values='reset database (delete all events)', tag=None, action=reset_db_action),
    ]
    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_RETURN, style=menu_style, action_dict=action_dict, commands=action_dict['commands'])
    menu.run()

def make_db():
    # Create an in memory sqlite database of hamburger options
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE event_recurrences (id INTEGER PRIMARY_KEY, name text, desc text)''')
    cursor.execute("INSERT INTO event_recurrences VALUES (1, 'none' ,'no recurrence')")
    cursor.execute("INSERT INTO event_recurrences VALUES (2, 'daily' ,'daily recurrence')")
    cursor.execute("INSERT INTO event_recurrences VALUES (3, 'weekly' ,'weekly recurrence')")
    cursor.execute("INSERT INTO event_recurrences VALUES (4, 'annual' ,'annual recurrence')")


    cursor.execute('''CREATE TABLE event_types (id INTEGER PRIMARY_KEY, name text, desc text, recurrence int)''')
    cursor.execute("INSERT INTO event_types VALUES (1, 'birthday' ,'a birthday event', 2)")
    cursor.execute("INSERT INTO event_types VALUES (2, 'anniversary' ,'an anniversary event', 2)")
    cursor.execute("INSERT INTO event_types VALUES (3, 'meeting', 'a meeting event', 1)")

    cursor.execute('''CREATE TABLE events (id INTEGER PRIMARY_KEY, date int, desc text, type int)''')
    conn.commit()
    return conn, cursor

if __name__ == '__main__':
    conn, cursor = make_db()
    menu_style = ci.TableStyle(show_cols=False, show_border=False)

    help_cmd = ci.GetInputCommand(help_cmd_action)
    cancel_cmd = ci.GetInputCommand(cancel_cmd_action)
    dow_cmd = ci.GetInputCommand(day_of_week_cmd_action)
    commands_std = { '/?': help_cmd, '/h': help_cmd, '/cancel': cancel_cmd, '/dow': dow_cmd }
    menu_style = ci.TableStyle(show_cols=False, show_border=False)
    action_dict = { 'conn': conn, 'cursor': cursor, 'commands': commands_std, 'num_events': 0 }

    menu_items = [
            ci.TableItem(col_values='Add an event', tag=None, action=add_event_action),
            ci.TableItem(col_values='List events', tag=None, action=list_event_action),
            ci.TableItem(col_values='Database submenu', tag=None, action=database_submenu_action)
        ]

    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_EXIT, style=menu_style, action_dict=action_dict, commands=commands_std)
    menu.run()