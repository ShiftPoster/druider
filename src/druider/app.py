import logging

from rich.logging import RichHandler
from rich.tree import Tree
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalGroup, Container
from textual.widget import Widget
from textual.widgets import Footer, Header, RichLog
from textual.widgets import TabbedContent, TabPane, Static

from druider.listing import Listing, Animals
from druider.data import load_data, DataType, EntryType, Column

logger = logging.getLogger(__name__)


class LoggingConsole(RichLog):
    file = False
    console: Widget

    def print(self, content):
        self.write(content)


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
    def __init__(self, rich_log_handler: RichHandler, *args, **kwargs):
        self.rich_log_handler = rich_log_handler
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Selected", id="details-selected-pane"):
                with VerticalGroup(name="Selected", id="logs", classes="box"):
                    yield Stats()
            with TabPane("Logs", id="details-logs-pane"):
                with VerticalGroup(name="Logs", id="logs", classes="box"):
                    # yield RichLog()
                    # yield Log()
                    yield self.rich_log_handler.console  # type: ignore


class Body(Vertical):
    """Application body."""

    data: DataType

    def __init__(self, rich_log_handler: RichHandler, data: DataType, *args, **kwargs):
        self.data = data
        self.details = Details(rich_log_handler, name="Details", id="details")
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

    def __init__(self, rich_log_handler: RichHandler, data: DataType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = Body(rich_log_handler, data, id="body")

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.body
        yield Footer()

    def on_mount(self):
        self.theme = "monokai"


if __name__ == "__main__":
    from pathlib import Path

    from textual.logging import TextualHandler

    FILE: Path = Path.cwd() / "data.csv"

    root = logging.getLogger()
    root.setLevel(1)
    rich_log_handler = RichHandler(
        console=LoggingConsole(),  # type: ignore
        rich_tracebacks=True,
    )
    root.addHandler(rich_log_handler)
    root.addHandler(TextualHandler())
    data = load_data(FILE)
    app = DruidHelper(rich_log_handler, data)
    app.run()
