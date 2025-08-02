import logging

from rich.tree import Tree
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalGroup
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

from druider.data import Column, DataType, EntryType
from druider.listing import Animals, Listing
from druider.logging import add_to_stdlib

logger = logging.getLogger(__name__)


class Stats(Container):
    def compose(self) -> ComposeResult:
        yield Static("Select animal for more details", id="stats")

    def get_tree(self, animal: EntryType) -> Tree:
        tree = Tree(animal[Column._name])
        for index, value in enumerate(animal):
            if index != Column._name and value:
                tree.add(f"{Column(index).title}: {value}")
        return tree

    def update_animal(self, animal: EntryType) -> None:
        self.query_one(Static).update(self.get_tree(animal))


class Details(Vertical):
    def __init__(self, *args, **kwargs):
        self.log_widget = add_to_stdlib()
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Selected", id="details-selected-pane"):
                with VerticalGroup(name="Selected", id="logs", classes="box"):
                    yield Stats()
            with TabPane("Logs", id="details-logs-pane"):
                with VerticalGroup(name="Logs", id="logs", classes="box"):
                    yield self.log_widget


class Body(Vertical):
    """Application body."""

    data: DataType

    def __init__(self, data: DataType, *args, **kwargs):
        self.data = data
        self.details = Details(name="Details", id="details")
        self.listing = Listing(data, name="Listing", id="listing")
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield self.listing
        yield self.details

    @on(Animals.CellSelected)
    def handle_selection(self, event: Animals.CellSelected):
        # TODO: workers? async def? definitely need something
        try:
            selected = self.query_one(Animals).select_animal(event)
            if selected is not None:
                logger.info(f"Passing to Stats: {selected}")
                self.query_one(Stats).update_animal(self.data[selected])
        except Exception as err:
            logger.critical(err)


class DruidHelper(App):
    CSS_PATH = "layout.tcss"

    def __init__(self, data: DataType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = Body(data, id="body")

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.body
        yield Footer()

    def on_mount(self):
        self.theme = "monokai"
