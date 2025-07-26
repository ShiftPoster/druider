import csv
from dataclasses import dataclass
from enum import IntEnum, auto
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Iterable, List, TypeVar

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer

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


@dataclass
class ColumnIndex:
    name: int
    type: int
    size: int

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


class TableApp(App):
    BINDINGS = [
        ("s", "sort_by_size", "Sort By Size"),
    ]

    file_handle: TextIOWrapper
    current_sorts: set = set()

    def compose(self) -> ComposeResult:
        yield DataTable()
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

    def filter_columns(self, index: ColumnIndex, columns: List[str]) -> Iterable[str]:
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
        table.zebra_stripes = True
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


app = TableApp()
if __name__ == "__main__":
    app.run()
