import csv
import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum, auto
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Iterable, List, TypeVar

from textual.containers import Container
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import DataTable
from textual.widgets._data_table import ColumnKey

from druid_helper.data import Column

logger = logging.getLogger(__name__)
T = TypeVar("T")
FILE: Path = Path.cwd() / "data.csv"


class Size(IntEnum):
    fine = auto()
    diminutive = auto()
    tiny = auto()
    small = auto()
    medium = auto()
    large = auto()
    huge = auto()
    gargantuan = auto()
    colossal = auto()

    @classmethod
    def parse(cls, value: str):
        return cls[value.lower()]


class Animals(DataTable):
    BORDER_TITLE = __name__
    current_sorts: set = set()
    _sorters: Dict[Column, Callable[[str], Any]] = {
        Column._name: sorted,
        Column.size: Size.parse,
    }
    _actions: Dict[Column, str] = {
        Column._name: "sort_by_name",
        Column.size: "sort_by_size",
    }
    zebra_stripes = True

    def add_data_column(self, column: Column) -> ColumnKey:
        return self.add_column(column.title, key=column.key)

    def add_data_columns(self) -> Iterable[ColumnKey]:
        return (
            self.add_data_column(Column.size),
            self.add_data_column(Column._name),
        )

    def on_mount(self) -> None:
        logger.info("hello world")
        self.add_data_columns()
        header = True
        # TODO: add key to rows
        with FILE.open(newline="") as fh:
            for line in csv.reader(fh):
                if header is True:
                    header = False
                else:
                    self.add_row(line[Column.size], line[Column._name])

    def sort_reverse(self, sort_type: str):
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def sort_data_column(self, column: Column):
        self.sort(column.key, key=self._sorters[column], reverse=self.sort_reverse(column.key))

    def action_sort_by_size(self) -> None:
        self.sort_data_column(Column.size)

    def action_sort_by_name(self) -> None:
        self.sort_data_column(Column._name)


class Listing(Container):
    def compose(self) -> ComposeResult:
        # TODO: yield sort and search
        yield Animals()

    @on(Animals.RowSelected)
    @on(Animals.CellSelected)
    @on(Animals.ColumnSelected)
    @on(Animals.HeaderSelected)
    @on(Animals.RowLabelSelected)
    def log_animal_selection(self, event):
        logger.debug(event)

    @on(Animals.HeaderSelected)
    def handle_header(self, event: Animals.HeaderSelected):
        # TODO: icon to indicate sort direction
        # FIXME: name sorting does not work correctly
        # https://textual.textualize.io/widgets/data_table/#sorting
        try:
            if event.column_key.value:
                column = Column[event.column_key.value]
                logger.info(f"Sorting Animals by {column!r}")
                self.query_one(Animals).sort_data_column(column)
        except Exception as err:
            logger.critical(err)

    @on(Animals.CellSelected)
    def handle_cell(self, event: Animals.CellSelected):
        try:
            if event.cell_key.column_key.value:
                if Column[event.cell_key.column_key.value] is Column._name:
                    logger.info(f"Caching Animal cell {event.value}")
        except Exception as err:
            logger.critical(err)
