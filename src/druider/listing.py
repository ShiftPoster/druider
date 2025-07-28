import logging
from collections.abc import Callable
from enum import IntEnum, auto
from typing import Any, Dict, Iterable, TypeVar

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable
from textual.widgets.data_table import ColumnKey

from druider.data import Column, DataType

logger = logging.getLogger(__name__)
T = TypeVar("T")


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
    data: DataType
    current_sorts: set = set()
    _sorters: Dict[Column, Callable[[str], Any]] = {
        Column._name: lambda s: s[0],
        Column.size: Size.parse,
    }
    _actions: Dict[Column, str] = {
        Column._name: "sort_by_name",
        Column.size: "sort_by_size",
    }
    zebra_stripes = True

    def __init__(self, data: DataType, *args, **kwargs) -> None:
        self.data = data
        super().__init__(*args, **kwargs)

    def add_data_column(self, column: Column) -> ColumnKey:
        return self.add_column(column.title, key=column.key)

    def add_data_columns(self) -> Iterable[ColumnKey]:
        return (
            self.add_data_column(Column.size),
            self.add_data_column(Column._name),
        )

    def add_data_rows(self):
        for index, entry in enumerate(self.data):
            if entry[Column.type] == "animal":
                self.add_row(entry[Column.size], entry[Column._name], key=str(index))

    def on_mount(self) -> None:
        logger.info("hello world")
        self.add_data_columns()
        self.add_data_rows()

    def sort_reverse(self, sort_type: str):
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def sort_data_column(self, column: Column):
        self.sort(
            column.key, key=self._sorters[column], reverse=self.sort_reverse(column.key)
        )

    def action_sort_by_size(self) -> None:
        self.sort_data_column(Column.size)

    def action_sort_by_name(self) -> None:
        self.sort_data_column(Column._name)

    def select_animal(self, event: DataTable.CellSelected) -> None | int:
        selected = None
        try:
            if event.cell_key.column_key.value:
                if Column[event.cell_key.column_key.value] is Column._name:
                    if event.cell_key.row_key.value is None:
                        raise ValueError(event.cell_key.row_key)
                    selected = int(event.cell_key.row_key.value)
                    logger.info(f"Animal selected: {event.value} ({selected})")
        except Exception as err:
            logger.critical(err)
        return selected


class Listing(Container):
    animals: Animals

    def __init__(self, data: DataType, *args, **kwargs) -> None:
        self.animals = Animals(data)
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        # TODO: yield sort and search
        yield self.animals

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
        try:
            if event.column_key.value:
                column = Column[event.column_key.value]
                logger.info(f"Sorting Animals by {column!r}")
                self.query_one(Animals).sort_data_column(column)
        except Exception as err:
            logger.critical(err)

    # @on(Animals.CellSelected)
    def _handle_cell(self, event: Animals.CellSelected):
        # NOTE: This may need to go on the app or body for values to be easily passed to details
        try:
            if event.cell_key.column_key.value:
                if Column[event.cell_key.column_key.value] is Column._name:
                    logger.info(f"Caching Animal cell {event.value}")
        except Exception as err:
            logger.critical(err)
