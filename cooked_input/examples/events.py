"""
Start of a DB/table example

Do example with event list manager

DB
Menu, submenu
Table
To gui

TODO list? description, project, priority, due date?
Event list (date, event, event type. Recurrence??)

table EventType - id Type Description
table Event - id date type description

how to do recurring - recurring boolean, date is first date, then frequency and unit
how to do date?

submenu to erase, load or dump the DB?
commands - /help, /cancel, /dayofweek (dow) date (day of week?)

"""

from datetime import datetime
import sqlite3
import cooked_input as ci

def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
    print('\nCommands:')
    print('\t/?, /h\tDisplay this help message')
    print('\t/cancel\tCancel the current operation')
    print('\t/dow [date]\tGet the day of the week for a date\n')
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
    raise NotImplementedError


def add_event_type_action(row, action_item):
    raise NotImplementedError


def add_event_action(row, action_item):
    raise NotImplementedError


def list_event_action(row, action_item):
    # list events... add a filter?
    raise NotImplementedError

def database_submenu_action(row, action_item):
    menu_items = [
        ci.TableItem(col_values='reset database (delete all events)', tag=None, action=reset_db_action),
    ]
    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_RETURN, style=menu_style, action_dict=action_dict, commands=action_dict['commands'])
    menu.run()

def make_db():
    # Create an in memory sqlite database of hamburger options
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE event_recurrences (id INTEGER PRIMARY_KEY, name text, desc text)''')
    cursor.execute("INSERT INTO event_recurrences VALUES (1, 'none' ,'no recurrence')")
    cursor.execute("INSERT INTO event_recurrences VALUES (2, 'annual' ,'annual recurrence')")
    cursor.execute("INSERT INTO event_recurrences VALUES (3, 'weekly' ,'weekly recurrence')")
    cursor.execute("INSERT INTO event_recurrences VALUES (4, 'daily' ,'daily recurrence')")

    cursor.execute('''CREATE TABLE event_types (id INTEGER PRIMARY_KEY, name text, desc text, recurring int)''')
    cursor.execute("INSERT INTO event_types VALUES (1, 'birthday' ,'a birthday event', 2)")
    cursor.execute("INSERT INTO event_types VALUES (2, 'anniversary' ,'an anniversary event', 2)")
    cursor.execute("INSERT INTO event_types VALUES (3, 'meeting', 'a meeting event', 1)")

    cursor.execute('''CREATE TABLE events (id INTEGER PRIMARY_KEY, date int, desc text, type int)''')
    return conn, cursor

if __name__ == '__main__':
    conn, cursor = make_db()
    menu_style = ci.TableStyle(show_cols=False, show_border=False)

    help_cmd = ci.GetInputCommand(help_cmd_action)
    cancel_cmd = ci.GetInputCommand(cancel_cmd_action)
    dow_cmd = ci.GetInputCommand(day_of_week_cmd_action)
    commands_std = { '/?': help_cmd, '/h': help_cmd, '/cancel': cancel_cmd, '/dow': dow_cmd }
    menu_style = ci.TableStyle(show_cols=False, show_border=False)
    action_dict = { 'conn': conn, 'cursor': cursor, 'commands': commands_std }

    menu_items = [
            # ci.TableItem(text, tag, action, item_data, hidden, enabled)
            ci.TableItem(col_values='Add an event type', tag=None, action=add_event_type_action),
            ci.TableItem(col_values='Add an event', tag=None, action=add_event_action),
            ci.TableItem(col_values='List events', tag=None, action=list_event_action),
            ci.TableItem(col_values='Database submenu', tag=None, action=database_submenu_action)
        ]

    menu = ci.Table(rows=menu_items, add_exit=ci.TABLE_ADD_EXIT, style=menu_style, action_dict=action_dict, commands=commands_std)
    menu.run()