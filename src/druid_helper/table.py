import csv
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum, auto
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Iterable, List, TypeVar

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header
from textual.widgets._data_table import ColumnKey

from druid_helper.data import Column

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


sorter: Dict[Column, Callable[[str], Any]] = {
    Column.size: Size.parse,
}


class Animals(DataTable):
    BINDINGS = [
        ("s", "sort_by_size", "Sort By Size"),
    ]
    current_sorts: set = set()

    def compose(self) -> Iterable[Widget]:
        yield DataTable(zebra_stripes=True)

    def add_data_column(self, column: Column) -> ColumnKey:
        return self.add_column(column.title, key=column.key)

    def add_data_columns(self) -> Iterable[ColumnKey]:
        return (
            self.add_data_column(Column._name),
            self.add_data_column(Column.size),
        )

    def on_mount(self) -> None:
        self.add_data_columns()
        self.add_row("tiger", "large")
        self.add_row("mouse", "tiny")

    def sort_data_column(self, column: Column):
        self.sort(column.key, key=sorter[column], reverse=self.sort_reverse(column.key))

    def sort_reverse(self, sort_type: str):
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def action_sort_by_size(self) -> None:
        self.sort_data_column(Column.size)


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


if __name__ == "__main__":
    from textual.widgets import Footer, Header

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
