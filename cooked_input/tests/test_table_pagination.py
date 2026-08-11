"""Tests for Table's pagination window and row lookup.

Everything here is pure state arithmetic on ``Table.table.start`` / ``.end`` plus a
print, so none of it needs scripted input and none of it can hang. That is why this
is the cheapest large block of get_table.py coverage available.

One thing to know before reading: ``Table.__init__`` does not populate ``_rows``.
``refresh_items()`` does, and ``get_table_choice()`` reaches it via
``_prep_get_input()``. A table that has not been refreshed reports zero rows, so
every test here refreshes first.

Len Wanger, 2026
"""

import pytest

from cooked_input import Table, TableItem, TableStyle


ROWS_PER_PAGE = 3
NUM_ROWS = 10


def make_table(num_rows=NUM_ROWS, rows_per_page=ROWS_PER_PAGE, **kwargs):
    """A single-column table of ``num_rows`` rows, tagged '0' through '<n-1>'."""
    rows = [TableItem([f"row {i}"], tag=str(i)) for i in range(num_rows)]
    table = Table(rows, col_names=["Value"], style=TableStyle(rows_per_page=rows_per_page), **kwargs)
    table.refresh_items()
    return table


def window(table):
    """The currently displayed row range as a (start, end) pair."""
    return table.table.start, table.table.end


@pytest.fixture
def table(capsys):
    """A paginated table. capsys swallows the renders the nav methods print."""
    return make_table()


class TestShowRows:
    def test_a_table_is_empty_until_it_is_refreshed(self):
        rows = [TableItem(["only row"])]
        assert Table(rows, col_names=["Value"]).get_num_rows() == 0

    def test_first_page_starts_at_the_top(self, table):
        table.show_rows(0)
        assert window(table) == (0, ROWS_PER_PAGE)

    def test_a_start_row_past_the_end_clamps_to_the_last_full_page(self, table):
        table.show_rows(99)
        # The last page is a full page ending on the final row, not a stub.
        assert window(table) == (NUM_ROWS - ROWS_PER_PAGE, NUM_ROWS)

    def test_a_negative_start_row_clamps_to_the_top(self, table):
        table.show_rows(-5)
        assert window(table) == (0, ROWS_PER_PAGE)

    def test_without_rows_per_page_the_whole_table_shows(self):
        table = make_table(rows_per_page=0)
        table.show_rows(0)
        assert window(table) == (0, NUM_ROWS)

    def test_a_page_larger_than_the_table_shows_every_row(self):
        table = make_table(num_rows=2, rows_per_page=ROWS_PER_PAGE)
        table.show_rows(0)
        assert window(table) == (0, 2)


class TestPageNavigation:
    def test_page_down_advances_one_page(self, table):
        table.show_rows(0)
        table.page_down()
        assert window(table) == (3, 6)

    def test_page_down_twice_advances_two_pages(self, table):
        table.show_rows(0)
        table.page_down()
        table.page_down()
        assert window(table) == (6, 9)

    def test_page_up_goes_back_one_page(self, table):
        table.show_rows(6)
        table.page_up()
        assert window(table) == (3, 6)

    def test_page_up_from_the_top_stays_at_the_top(self, table):
        table.show_rows(0)
        table.page_up()
        assert window(table) == (0, ROWS_PER_PAGE)

    def test_page_down_from_the_end_stays_at_the_end(self, table):
        table.goto_end()
        table.page_down()
        assert window(table) == (NUM_ROWS - ROWS_PER_PAGE, NUM_ROWS)

    def test_goto_end_shows_the_last_page(self, table):
        table.goto_end()
        assert window(table) == (7, 10)

    def test_goto_home_shows_the_first_page(self, table):
        table.goto_end()
        table.goto_home()
        assert window(table) == (0, ROWS_PER_PAGE)

    def test_navigation_renders_the_table(self, table, capsys):
        table.show_rows(0)
        capsys.readouterr()
        table.page_down()
        assert "row 3" in capsys.readouterr().out


class TestSingleRowScrolling:
    # Regression guards for #46: these two bodies used to be the wrong way round, so a
    # command bound to "scroll up one row" scrolled the view down. User-visible, because
    # Table._get_choice wires UpOneRowRequest straight to scroll_up_one_row.

    def test_scroll_up_one_row_moves_toward_earlier_rows(self, table):
        table.show_rows(5)
        table.scroll_up_one_row()
        assert window(table) == (4, 7)

    def test_scroll_down_one_row_moves_toward_later_rows(self, table):
        table.show_rows(0)
        table.scroll_down_one_row()
        assert window(table) == (1, 4)

    def test_scrolling_up_agrees_with_paging_up(self, table):
        # The pair now moves the same way as page_up and page_down, just by one row.
        table.show_rows(5)
        table.scroll_up_one_row()
        after_scroll = window(table)[0]

        table.show_rows(5)
        table.page_up()
        assert after_scroll > window(table)[0]

    def test_scrolling_up_stops_at_the_first_row(self, table):
        table.show_rows(0)
        table.scroll_up_one_row()
        assert window(table) == (0, 3)

    def test_scrolling_down_stops_at_the_last_row(self, table):
        table.goto_end()
        table.scroll_down_one_row()
        assert window(table) == (NUM_ROWS - ROWS_PER_PAGE, NUM_ROWS)


class TestRowLookup:
    def test_get_num_rows_counts_every_row(self, table):
        assert table.get_num_rows() == NUM_ROWS

    def test_get_row_finds_a_row_by_tag(self, table):
        assert table.get_row("3").tag == "3"
        assert table.get_row("3").values == ["row 3"]

    def test_get_row_raises_for_an_unknown_tag(self, table):
        with pytest.raises(ValueError, match="not in the table"):
            table.get_row("nope")

    def test_get_action_returns_the_rows_action(self, table):
        # Rows built without an explicit action carry the default sentinel.
        assert table.get_action("3") == "default"

    def test_get_action_raises_for_an_unknown_tag(self, table):
        with pytest.raises(ValueError, match="not in the table"):
            table.get_action("nope")


class TestDoAction:
    def test_a_callable_action_is_called_with_the_row_and_action_dict(self):
        calls = []

        def record(row, action_dict):
            calls.append((row.tag, action_dict))
            return "called"

        action_dict = {"key": "value"}
        rows = [TableItem(["a row"], tag="1", action=record)]
        table = Table(rows, col_names=["Value"], action_dict=action_dict)
        table.refresh_items()

        assert table.do_action(table.get_row("1")) == "called"
        assert calls == [("1", action_dict)]

    def test_the_default_sentinel_falls_through_to_the_tables_default_action(self):
        rows = [TableItem(["a row"], tag="1")]
        table = Table(rows, col_names=["Value"], default_action=lambda row, ad: f"default for {row.tag}")
        table.refresh_items()

        assert table.do_action(table.get_row("1")) == "default for 1"

    @pytest.mark.parametrize("action", ["exit", "return"])
    def test_an_exit_row_yields_no_selection(self, action):
        # Regression guard for #47: 'exit' is neither callable nor the default sentinel,
        # so do_action used to fall through and hand back the TableItem -- which is why
        # get_menu's `result == 'exit'` test could never be true.
        rows = [TableItem(["a row"], tag="1", action=action)]
        table = Table(rows, col_names=["Value"])
        table.refresh_items()

        assert table.do_action(table.get_row("1")) is None

    def test_a_row_with_an_unrecognised_action_comes_back_unchanged(self):
        rows = [TableItem(["a row"], tag="1", action="something else")]
        table = Table(rows, col_names=["Value"])
        table.refresh_items()

        row = table.get_row("1")
        assert table.do_action(row) is row
