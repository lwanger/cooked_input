
"""
Test cooked_input commands

Len Wanger, 2017

TODO test commands

    - examples using cmd_str and cmd_vars
    - actions: from .get_input import COMMAND_ACTION_USE_VALUE, COMMAND_ACTION_CANCEL, COMMAND_ACTION_NOP
    - tables - page_up, down,etc.
    - add exit command type

    from .get_input import GetInputInterrupt
    from .get_input import RefreshScreenInterrupt
"""

import cooked_input as ci

def show_help_action(cmd_str, cmd_vars, cmd_dict):
    print('Help Message:')
    print('-------------\n')
    print('/h, /?  - show this message')
    print('/cancel - cancel this operation')
    print('/red    - use red as a value\n')
    return (ci.COMMAND_ACTION_NOP, None)

def cancel_action(cmd_str, cmd_vars, cmd_dict):
    print('\nCANCELLING OPERATION\n')
    return (ci.COMMAND_ACTION_CANCEL, None)


def use_red_action(cmd_str, cmd_vars, cmd_dict):
    return (ci.COMMAND_ACTION_USE_VALUE, 'red')


if __name__ == '__main__':
    prompt_str = 'Color (cmds /h, /?, /cancel, /red)'
    colors = ['red', 'blue', 'green', 'yellow', '/?']
    rows = [ci.TableItem(val) for val in colors]
    show_help_cmd = ci.GetInputCommand(show_help_action)

    cmds = {
            '/h': show_help_cmd,
            '/?': show_help_cmd,
            '/cancel': ci.GetInputCommand(cancel_action),
            '/red': ci.GetInputCommand(use_red_action, {'color': 'red'})
        }

    if False:
        try:
            result = ci.get_string(prompt=prompt_str, commands=cmds)
            print('result={}'.format(result))
        except ci.GetInputInterrupt:
            print('Got GetInputInterrupt')

    try:
        # tbl = ci.Table(rows, col_names=['Color'], prompt=prompt_str, default_action=ci.TABLE_DEFAULT_ACTION_FIRST_VAL)
        tbl = ci.Table(rows, col_names=['Color'], prompt=prompt_str, add_exit=False, default_action=ci.TABLE_DEFAULT_ACTION_FIRST_VAL, commands=cmds)
        result = ci.get_table_input(tbl)
        print('result={}'.format(result))
    except ci.GetInputInterrupt:
        print('Got GetInputInterrupt')

    try:
        tbl = ci.Table(rows, col_names=['Color'], prompt=prompt_str, default_action=ci.TABLE_DEFAULT_ACTION_FIRST_VAL, commands=cmds)
        tbl.run()
    except ci.GetInputInterrupt:
        print('Got GetInputInterrupt')
