.. currentmodule:: cooked_input

Cooked Input Tutorial, Part Two
*******************************

Introduction:
=============

This is the second part of the tutorial for ``cooked_input``. It assumes that you have completed the first
part of the `tutorial <tutorial.html>`_. In this tutorial you
will create a simple, menu driven, application that demonstrates some of cooked_input's
advanced features: tables, menus, and commands.

To start we will import cooked_input and create lists to hold event types and events

.. code-block:: python

    from collections import namedtuple
    import cooked_input as ci

    EventType = namedtuple('EventType', 'id name desc')
    Event = namedtuple('Event', 'id date desc type')

    event_types = [
        EventType(1, 'birthday' ,'a birthday event'),
        EventType(2, 'anniversary' ,'an anniversary event'),
        EventType(3, 'meeting', 'a meeting event')
    ]
    events = []

Commands:
=========

Next we will create some commands for the application. A cooked_input command is a string the user can enter
during a cooked_input input request that calls a callback function.

Commands are specified by by passing a dictionary, where the key is the string and the value is
a :class:`GetInputCommand` instance, to the ``commands`` parameter of a cooked_input input call.
``GetInputCommand`` objects consist of a callback function and an optional dictionary of values to be sent to the
callback (``cmd_dict``). Command callbacks take three input parameters (``cmd_str``, ``cmd_vars``, and ``cmd_dict``)
and return a ``CommandResponse`` tuple. ``cmd_str`` and ``cmd_vars`` are the command and any parameters after the
command, and ``cmd_dict`` is the dictionary specified in the ``GetInputCommand``. ``CommandResponse``
is a tuple where the first value is the return type of the command and the second value the value returned by the
command.

For example, the following code creates a ``/in_to_mm`` command to convert from inches to millimeters
and supplies the result as the input:

.. code-block:: python

    def in_to_mm_cmd_action(cmd_str, cmd_vars, cmd_dict):
        mm = int(cmd_vars) * 25.4  # 1 inch is 25.4 millimeters
        return ci.CommandResponse(ci.COMMAND_ACTION_USE_VALUE, str(mm))

    cmds = {'/in_to_mm': ci.GetInputCommand(in_to_mm_cmd_action)}
    v = ci.get_float(prompt="How long is it (in mm)", commands=cmds)
    print(v)

Running the code, we can use the command to use 2 inches as the input::

    >>> How long is it (in mm): /in_to_mm 2
    >>> 50.8

In addition to commands that return values, there are ``CommandResponses`` for purely informational
commands (**COMMAND_ACTION_NOP**) and cancellation commands (**COMMAND_ACTION_CANCEL**).

Let's go ahead and add two commands to the event manager application. The first displays a help message help, and the
second to cancel the current operation:

.. code-block:: python

    def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
        help_str = """
            Commands:
                /?, /help   Display this help message
                /cancel     Cancel the current operation
        """
        print(help_str)
        return ci.CommandResponse(ci.COMMAND_ACTION_NOP, None)

    def cancel_cmd_action(cmd_str, cmd_vars, cmd_dict):
        if ci.get_yes_no(prompt='Are you sure?', default='no') == 'yes':
            print('\nCommand cancelled...')
            return ci.CommandResponse(ci.COMMAND_ACTION_CANCEL, None)
         else:
            return ci.CommandResponse(ci.COMMAND_ACTION_NOP, None)

    help_cmd = ci.GetInputCommand(help_cmd_action)
    cancel_cmd = ci.GetInputCommand(cancel_cmd_action)
    commands_std = { '/?': help_cmd, '/h': help_cmd, '/cancel': cancel_cmd }

.. note::
    As was done in the help command, you can have more than one command point to the same command ``GetInputCommand``.
    Also, as was done in the cancel commands, you can call ``cooked_input`` functions within a command callback.

More detail about cooked_input commands can be found at: `command <get_input_commands.html>`_

Tables:
=======

cooked_input can also display tables of data. The easiest way to create a table is to use the :func:`create_table`
convenience function. ``create_table`` can create a table any iterable where the fields in each item can be fetched
by field or attribute name, including: objects, dictionaries, and namedtuples.

``create_table`` requires two parameters: ``items``, an iterable containing row data for the table, and ``fields``, the
list of which fields/attributes from the items to show as columns in the table.

Once created, the table can be displayed using its ``show_table`` method:

.. code-block:: python

    flds = ['name', 'desc']
    tbl = ci.create_table(items=event_types, fields=flds)
    tbl.show_table()

will display::

    +-------------+----------------------+
    |        name | desc                 |
    +-------------+----------------------+
    |    birthday | a birthday event     |
    | anniversary | an anniversary event |
    |     meeting | a meeting event      |
    +-------------+----------------------+

There are several other common parameters for ``create_table``. ``field_names`` is a list of strings to use for the
column headers, `title` sets a title for the table, and ``style`` specified a :class:`TableStyle` for used when
displaying the table.

You can also use tables for input by either calling the the :func:`get_table_input` convenience function, or the
table's ``get_table_choice`` method. You can see this in action by trying the following:

.. code-block:: python

    >>> v = ci.get_table_input(tbl, prompt='event type')
    >>>
    >>> +-------------+----------------------+
    >>> |        name | desc                 |
    >>> +-------------+----------------------+
    >>> |    birthday | a birthday event     |
    >>> | anniversary | an anniversary event |
    >>> |     meeting | a meeting event      |
    >>> +-------------+----------------------+
    >>>
    >>> event type: m
    >>> >>> print(v)
    >>> TableItem(col_values=['a meeting event'], tag=meeting, action=default, item_data=None, hidden=False, enabled=True)

.. note::
    Notice that we only had to type in 'm' to choose ``meeting``, ``get_table_choice`` automatically adds
    a `ChoiceCleaner <cleaners.html>`_ as a convenience!

Each row in a cooked_input table is a :class:`TableItem`, and by default ``get_table_choice`` will return the
`TableItem` for the choice entered. This can be modified by setting the ``default_action`` parameter, For instance,
setting ``default_action`` to **TABLE_RETURN_FIRST_VAL** would have returned "meeting" in the example above.

.. note::
    ``create_table`` can create a table by passing in the query from an ORM-managed database such
    as `SQLAlchemy <http://www.sqlalchemy.org>`_. When doing so it's useful to set the ``add_item_to_item_data``
    parameter in ``create_table`` to **True**. This will automatically attach the full data
    for the item to the row's item_data. In the example above
    the ``id`` for the event_type is not in the table. By setting ``add_item_to_item_data`` = **True** it
    could be accessed by through ``v.item_data['item']['id']``. This makes it easy to get the primary key
    of the choice's database entry even though it's not shown in the table.

The default action for the table can also be set to a function or callable. The action callback receives
two input parameters. ``Row`` contains the ``TableItem`` for the row chosen, which includes a
``values`` field containing the columns values for the row. The callback function also receives
``action_data`` which is an optional dictionary of values to send to the action. For instance,
we can send a capitalized version of the event type with the following default action callback

.. code-block:: python

    def cap_action(row, action_item):
        val = row.tag.upper()
        return val

    tbl = ci.create_table(event_types, flds, default_action=cap_action)

would produce::

    >>> +-------------+----------------------+
    >>> |        name | desc                 |
    >>> +-------------+----------------------+
    >>> |    birthday | a birthday event     |
    >>> | anniversary | an anniversary event |
    >>> |     meeting | a meeting event      |
    >>> +-------------+----------------------+
    >>>
    >>> event type: a
    >>> ANNIVERSARY

Lets create some action callbacks to out application to: add an event, list all of the events and delete all of the events:

.. code-block:: python

    def reset_db_action(row, action_item):
        cmds = action_dict['commands']
        if ci.get_yes_no(prompt='Delete all events? ', default='no',
                            commands=cmds) == 'yes':
            action_dict['events'] = []

    def add_event_action(row, action_item):
        events = action_dict['events']
        event_types = action_dict['event_types']
        cmds = action_dict['commands']
        desc = ci.get_string(prompt="Event description? ", commands=cmds)
        tbl = ci.create_table(event_types, ["name", "desc"], ["Name", "Desc"],
            add_item_to_item_data=True)
        event_type = tbl.get_table_choice(prompt='Type? ', commands=cmds'])
        date = ci.get_date(prompt='Date? ', default='today', commands=cmds)
        type_id = event_type.item_data['item'].id
        events.append(Event(len(events)+1, date, desc, type_id))

    def list_event_action(row, action_item):
        events = action_dict['events']
        event_types = action_dict['event_types']

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

.. note::
    These action callbacks depend on receiving the commands, events and event_types lists in ``action_dict``.
    Action_dict provides a method of sending data to and from the callback without using global variables. This
    mechanism is useful to provide context such as: database sessions/connections, user information, etc.

Menus:
======

The final piece of the application is to add menus. In cooked_input menus are tables where the action callback
performs the action for the menu item. The ``run`` method on tables loops calling ``get_table_choice``. By default
the menu will loop indefinately. A menu option to exit the menu can be added by setting the ``add_exit`` parameter
to **TABLE_ADD_EXIT** when creating the table.

Submenus can be created by running a table from a menu item action callback and setting the ``add_exit`` parameter
to **TABLE_ADD_RETURN** when creating the table.

Let's finish the application by adding a main menu and database submenu:

.. code-block:: python

    def db_submenu_action(row, action_item):
        style = action_dict['menu_style']
        items = [ ci.TableItem('Delete all events', action=reset_db_action) ]
        menu = ci.Table(rows=items, add_exit=ci.TABLE_ADD_RETURN, style=style,
            action_dict=action_dict)
        menu.run()

    if __name__ == '__main__':
        style = ci.TableStyle(show_cols=False, show_border=False)
        action_dict = { 'events': events, 'event_types': event_types,
            'commands': commands_std, , 'style': style }

        items = [
                ci.TableItem('Add an event', action=add_event_action),
                ci.TableItem('List events', action=list_event_action),
                ci.TableItem('Database submenu', action=db_submenu_action)
            ]
        menu = ci.Table(rows=items, add_exit=ci.TABLE_ADD_EXIT, style=style,
            action_dict=action_dict)
        menu.run()

Running the application:
========================

Try running the application (the full code is available at `events.py <events.html>`_). You can test adding
events and listing them. Don't forget to try the commands. For example, start adding event and type
**\\cancel** to stop in the middle of the operation without adding the event.

You may also want to try adding a new menu item to the database menu to add an event type. You'll see just how
easy it is to add new functionality to an application with cooked_input.

From Here:
==========

That completes the second part of the cooked_input tutorial. For more information take a look at the
`how-to/FAQ <how_to.html>`_ section of the documentation. You can also look at the various examples.

