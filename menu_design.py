"""
Menu & Table design notes

Len Wanger, 2017

Design:

Tabless:
========

- Design a table viewer (that can be the basis of menus):
    - CITable is a list of SubTable types. These are:
        - Data at the Table level? list of data_tables (subtables), Title, page info, display/render method?
        - need way to link displayed row to underlying table data (e.g. 10th row of 3rd page of table is row X of the table).
        - Paging for long pages: rows/page, current page, filter, etc. Show summary ("page x or y, displaying i to j"
            or "found X records, displaying i to j" on top or bottom) (Look at flask pagination)
        - Scrolling for wide pages
        - SubTable:
            - has column names, style, a header, a footer, and a SubTableDataBlock
            - can override style in header, footer  and data block
            - style allow pattern for row/column shading (i.e. background color for row % i
            - CITableHeader - used for headers (or headers and footers?). text/title,, can have col names, page info, borders
            - CITableFooter - used for footers and sub-total lines, summary statistics. col names, border, page info
            - SubTableDataBlock
                - Used for Rows. Each row has data (or function to get data), formatting, borders, header/footers,
                    - cleaning functions
                        - cleaning examples: Nan value, default value, scaling
                    - formatting: width, alignment, foreground and background color, etc.
                    - control for borders - top, bottom, left, right (with none, single, heavy, etc.) - like excel?
                - support static (read at creation) or Dynamic refreshed on every render tables
                - Filter functions to filter/select rows - can be used to hide or disable rows. Can be used as search
                    function (by any Validator)
                - Columns have a 'visible' boolean
                - Each column can have: width, style, alignment, format string, etc.
                - Can tell number of rows
                - Can sort rows
                - Can filter rows/cols - can make rows - disabled (grayed out) or invisible.
                - support summary statistics such as count, total, subtotal, min, max, mean, stddev, for header/footer
                - Block types for: lists/dicts/named tuples, csv, json, PrettyTable, DB/SQLAlchemy, and Pandas data frames.
                    Block types for text/spacers (not selectable).
        - render methods: screen, curses (redraw in place), pdf (reportlab), html, GUI, silent (not shown)?
        - questions:
            - define borders types (horizontal and vertical): none, thin, thick, double line, dashes, etc.?
            - how to deal with different width sub-tables? Ragged, stretch to widest?
        - start:
            - text rendering only
            - single header, datablock, footer
            - horizontal, vertical borders (and juncions)
            - specify columns w/ width and format strings
            - sort function - with cmp function? Allow reverse and secondary and tertiary sorts
            - summary statistics
            - convenience functions for simpletable(from list/dict/tuple), menu
        - next:
            - multiple data blocks
            - csv and database import
            - convenience functions for simpletable(from db or csv)
            - paging
            - search /filter function
            - hide columns
            - support default selection row in table
        - next:
            - curses
            - navigation - up/down, next_page/prev_page, first_page/last_page
            - row shading (pattern of foreground/background)
            - dynamic tables
        - next:
            - selections - single, multiple (shift), multiple discontinuous (ctrl) of rows/columns
            - display ellipses (e.g. n rows of head, ..., n rows of tail.)
            - pdf output
        - more advanced:
            - edit cell, cut, copy, paste row/col
        - future / don't do:
            - wrapping values that are too wide (plus vertical alignment in a cell
            - support forms - then use get_input like wtform
            - split/join cells

    - scenarios:
        - menus
        - simple database table with 2 columns
        - db table with more than 2 columns
        - table with more than one page
        - table with sub-totals
        - Celcius to Farenheit dynamic table!
        - print utf-8 character table! good sample for long table, filter (by row range, unicodedata name, etc.), and search.
            import unicodedata
            def print_u_table(start, stop):
                for i in range(start, stop):
                    c = chr(i)
                    try:
                        print(f'{i:3d}\t{c}\t{unicodedata.name(c)}\t{unicodedata.category(c)}')
                    except ValueError:
                        print(f'ValueError: {i}')

    - reference material:
        - prettytable - https://github.com/kxxoling/PTable/blob/master/docs/tutorial.rst
            - tables: border=t/f, header=t/f, hrules=t/f, vrules=t/f, intformat, floatformat, padding_width,
                left_padding_width, right_padding_width, vertical_char, horizontal_char, junction_char
            - pt.field_names = []
            - pt.add_row('field_name', [values])
            - pt.del_row(), pt.clear() and pt.clear_rows()
            - print, print_html
            - pt.get_string(fields=[], start=i, end=j, sort_by='field name')
            - for columns: x.align = 'l', 'r' or 'c'
            - from_csv function to add CSV data
            - from database:
                import sqlite3
                from prettytable import from_db_cursor

                connection = sqlite3.connect("mydb.db")
                cursor = connection.cursor()
                cursor.execute("SELECT field1, field2, field3 FROM my_table")
                mytable = from_db_cursor(cursor)
        - very simple: https://github.com/jcalazan/format-table/blob/master/format_table.py
        - https://tableprint.readthedocs.io/
            - look at styles.py for table and row styles. hline and vline:
                        note: unicodedata.lookup('BLACK SQUARE')
                        top=LineStyle('◢', '■', '■', '◣'),
                        below_header=LineStyle(' ', '━', '━', ' '),
                        bottom=LineStyle('◥', '■', '■', '◤'),
                        row=LineStyle(' ', '', ' ', ' '),
            - table, table_context, header, row
            - define table header, with columns. Each column has width and style
            - has tableprint.header([header], width, style, header_str, show_header=True),
            tableprint.row([values], width, fmt_spec, style), tableprint.bottom, tableprint.banner(msg, width, style)
            - has out for file-like object to sent it to (default: sys.stdout)
        - Just use VeryPrettyTable? https://github.com/smeggingsmegger/VeryPrettyTable
        - https://github.com/absltkaos/python-dynamic-table
            - methods: print_header, print_table, print_row, print_rows, print_footer
            - pass in a table_renderer - text, csv, html
            - has TableFilters, with: filter_table, set_col_rule, add_row_rule
            - renderers have: indent, borderless, color_disabled, padding, padding_char, h_border_char, v_border_char
                col_sep_char
        - Reportlab:
            - way too much... make compatible subset
            - text, lines, colors (background and fill), style, fonts (name, size, style)
            - word spacing, line spacing
            - lines, with style and endcap
            - paragraph styles, doc templates, ...
            - tables: data, colwidths, rowheights, style, splitbyrow, repeatrows, repeatcols, rowsplitrange, spacebefore, spaceafter)
                - table_style: line_above, line_below, align, etc.

Menus:
======

- Lots of ideas from CursesMenu.

class Menu(object):
    title (str)
    set of menu items (list of MenuItems)

    def __init__(self, title, items=None, **options):
        # options:  add_exit_item (automatically put exit item last), repeat, show_function (for displaying the menu)

    def __repr__(self, function):

    def show(self):
    def add_item(self):
    def remove_item(self):

class DynamicMenu(Menu):
    # takes refresh_items function for generating list of items
    def __init__(self, title, item_function=None, item_function_args,  item_function_kwargs, **options):

class MenuItem(object):
    # abstract base class for MenuItems
    def __init__(self, args, kwargs, **options):
        # options:
        #   disabled: grayed out and not selectable
        #   visible: to make visible/invisiable (not shown)

    def __repr__(self)


class SelectionItem(MenuItem, **options):
    # returns a tag when selected
    def __init__(self, tag):

class FunctionItem(MenuItem, args, kwargs, **options):
    # menu item that calls a callable (function, lambda, or class method)
    # args and kwargs are passed as parameters to the callable
    def __init__(self, text, function, args, **options):

class SubMenuItem(MenuItem):
    def __init__(self, menu, parent, **options):

class SpacerItem(MenuItem):
    # This is not selectable, just for formatting (space or text)
    def __init__(self, text, **options):

class ExitItem(MenuItem):
    # Exits when called
    def __init__(self, text, **options):

class BackItem(MenuItem):
    # Reverts back to parent menu
    def __init__(self, text, **options):


class CITable(object):
    # abstract base class for tables?

<lots more table stuff to do!>
<is a menu a CITable (or subclass) with a menu_displayer display function?>

TODO:
    - Should exit be a SelectionItem or Boolean to add automatically (or both...)
    - How to integrate cleaning and validating?
    - How to set default row/item? None for no default
    - How to have multple choices in a table (crtl to pick multiple rows, shift to pick multiple contiguous rows)
    - Add indent with SpacerItem (so everything below is indented?
    - SpacerItem to BorderItem, with border type (blank for space), test, indent-level, etc. Makes a non-selectable item
        in the menu (up/down to skip it.)
    - Separate ExitItem, or exit_when_selected parameter on selection item?
    - Separate BackItem, or have action for return_to_parent? Could have NavigationItems that has actions for: exit,
        pop_to_parent, or pop_to_top_menu
    - need a get_return() function for the menu? Seems like bad design if needed.
    - General flow:  create menu items, create menu, call menu_show. Or just result = menu.show in a while loop?
    - How to handle actions for non-Function Items (have a action_handler function?) by default return the value?
        They could take a handler function that receives the value tag as a parameter.
    - How to remove/change items in the menu? Should items have a tag?
    - How to page long menus?
    - m.success string for showing success? Or handler just prints (can have flash_messages type of structure for msgs
        from the handler)
    - When sub-menu is called it should have caller/parent passed in plus context info. Then knows where to pop back to
        (so can support being called from many-to-one relationship).
    - Add navigation cmds like menu (dafvid on Github): 'p' - previous item or page, 'n' - next item/page, # for item #,
        'u' - update dynamic menu, 'h' - home/top menu, 'b' - back to parent menu, 'q' - quit, '?' - help
    - Add curses support so menu stays in place and can navigate with arrow keys, then hit select? Bold the current selection,
        default item starts on that item.
    - Work on table getter - display table in curses environment (arrows up/down, next and prev page, etc.) Allow filter
        to search for rows matching criteria (e.g. a Validator), allow render function to be passed in. Make a row_fetcher
        function (like DynamicItem) to get the data from a: list, pretty)_table, database query, Pandas dataframe, ... .
        Allow tab/sh-tab to traverse columns
    - different display functions (i.e. function for displaying the table - silent_table for no display of menu or table),
        can have pretty_table by default (or a curses equivalent) - have curses and non-curses options
    - Use curses for menu and tables, so can refresh in place, highlight current row/col, etc.
    - How to do requirements for curses in Windows?
    - Convenience functions for DynamicMenu (item_fetcher function), ListMenu (all SelectionItems and one handler
        function), FunctionMenu (all FunctionItems), PageMenu (multiple pages), etc.
    - Allow f-strings for prompt (and/or menu text), with kwargs passed in to display function (so can do config menu
        like things - f"edit profile for '{user}'" for "2. edit profile for 'lenw'"
    - For tables, have the concept of slicers - for both rows and columns (rows=start:stop:step, columns=start:stop:step).
        allow elipses (show 1st n and or last n rows or columns and elipses in between). Like head and tail.
    - For tables allow a sort method and sorted option
    - For tables allow showing summary statistics - count, total, sub-total, mean, max, min, mode, median?

    - Examples/scenarios:
        - menus:
            - example runner
            - simple menu (numbered item built from list)
            - action functions (with args/kwargs for context)
            - sub-menus
            - different borders
            - sub-menu with multiple parents
            - pick-once and quit
            - loop w/ pick until quit picked
            - dynamic menu - from: list, pretty-table, database, Pandas
            - different display functions (i.e. function for displaying the table - silent_table for no display of menu or table)
            - filter functions (i.e. only choices matching a role)
            - set user profile - list users, add profile, edit profile
            - use lambda for actions
        - tables:
            - list, pretty-table database, Pandas
            - different borders
            - format columns (width) and rows (length)
            - formats - bold, color, etc. for headers and borders
            - long table (multiple pages)
            - wide table (scroll to see columns)
            - wide table (filter columns shown)
            - search/filter by keyword
            - different display functions
            - filter rows/columns with filter function (e.g. don't show passwords, only certain roles can see certain data)
            - optional edit value - have edit_function to edit the cell value - e.g. change user name, when enter hit does
                database function to change it.
            - optional delete row - delete_function to delete the row (have cut-and-paste functions?)
"""
