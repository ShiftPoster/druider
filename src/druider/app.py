import logging

from rich.logging import RichHandler
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalGroup
from textual.widget import Widget
from textual.widgets import Footer, Header, RichLog
from textual.widgets import TabbedContent, Placeholder, TabPane

from druider.listing import Listing

logger = logging.getLogger(__name__)


class LoggingConsole(RichLog):
    file = False
    console: Widget

    def print(self, content):
        self.write(content)


class Details(Vertical):
    def __init__(self, rich_log_handler: RichHandler, *args, **kwargs):
        self.rich_log_handler = rich_log_handler
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Selected", id="details-selected-pane"):
                with VerticalGroup(name="Selected", id="logs", classes="box"):
                    yield Placeholder()
            with TabPane("Logs", id="details-logs-pane"):
                with VerticalGroup(name="Logs", id="logs", classes="box"):
                    # yield RichLog()
                    # yield Log()
                    yield self.rich_log_handler.console  # type: ignore


class Body(Vertical):
    """Application body."""

    def __init__(self, rich_log_handler: RichHandler, *args, **kwargs):
        self.details = Details(rich_log_handler, name="Details", id="details")
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Listing(name="Listing", id="listing")
        yield self.details


class DruidHelper(App):
    CSS_PATH = "layout.tcss"

    def __init__(self, rich_log_handler: RichHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = Body(rich_log_handler, id="body")

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.body
        yield Footer()

    def on_mount(self):
        self.theme = "monokai"


if __name__ == "__main__":
    from textual.logging import TextualHandler

    root = logging.getLogger()
    root.setLevel(1)
    rich_log_handler = RichHandler(
        console=LoggingConsole(),  # type: ignore
        rich_tracebacks=True,
    )
    root.addHandler(rich_log_handler)
    root.addHandler(TextualHandler())
    app = DruidHelper(rich_log_handler)
    app.run()
