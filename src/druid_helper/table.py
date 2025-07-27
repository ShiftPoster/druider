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


if __name__ == "__main__":
    from textual.widgets import Footer, Header

    @dataclass
    class ColumnIndex:
        name: int
        size: int
        type: int

        def indecies(self) -> Iterable[int]:
            return self.__dict__.values()

        def columns(self) -> Iterable[str]:
            return self.__dict__.keys()

        @classmethod
        def parse(cls, header: List[str]):
            kwargs = {}
            refernce = tuple(map(str.upper, header))
            for attr in cls.__annotations__:
                kwargs[attr] = refernce.index(attr.upper())
            return cls(**kwargs)

    class AnimalApp(App):
        BINDINGS = [
            ("s", "sort_by_size", "Sort By Size"),
        ]

        file_handle: TextIOWrapper
        current_sorts: set = set()

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield DataTable(zebra_stripes=True)
            yield Footer()

        def sort_reverse(self, sort_type: str):
            """Determine if `sort_type` is ascending or descending."""
            reverse = sort_type in self.current_sorts
            if reverse:
                self.current_sorts.remove(sort_type)
            else:
                self.current_sorts.add(sort_type)
            return reverse

        def action_sort_by_size(self) -> None:
            table = self.query_one(DataTable)
            table.sort(
                "size",
                key=lambda s: Size.parse(s),
                reverse=self.sort_reverse("size"),
            )

        def filter_columns(
            self, index: ColumnIndex, columns: List[str]
        ) -> Iterable[str]:
            yield from (col for col in columns if col.lower() in index.columns())

        def verify_row(self, index: ColumnIndex, line: List[str]) -> bool:
            rv = True
            if line[index.type].upper() != "animal".upper():
                rv = False
            return rv

        def map_row(self, index: ColumnIndex, row: List[str]) -> Iterable[str]:
            return (row[i] for i in index.indecies())

        def on_mount(self) -> None:
            table = self.query_one(DataTable)
            index = None
            for line in csv.reader(self.file_handle):
                if index is None:
                    index = ColumnIndex.parse(line)
                    for title in self.filter_columns(index, line):
                        table.add_column(title, key=title.lower())
                elif self.verify_row(index, line):
                    table.add_row(*self.map_row(index, line))

        def run(self, *args, **kwargs) -> Any:
            rv = None
            with FILE.open(newline="") as fh:
                self.file_handle = fh
                rv = super().run(*args, **kwargs)
            return rv

    AnimalApp().run()
