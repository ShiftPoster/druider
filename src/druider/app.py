import logging

from rich.logging import RichHandler
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalGroup
from textual.widget import Widget
from textual.widgets import Footer, Header, RichLog

from druider.listing import Listing

logger = logging.getLogger(__name__)


class LoggingConsole(RichLog):
    file = False
    console: Widget

    def print(self, content):
        self.write(content)


class Body(Vertical):
    """Application body."""

    def __init__(self, rich_log_handler: RichHandler, *args, **kwargs):
        self.rich_log_handler = rich_log_handler
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Listing(name="Listing", id="listing")
        with Container(name="Details", id="details", classes="box"):
            with VerticalGroup(name="Logs", id="logs", classes="box"):
                # yield RichLog()
                # yield Log()
                yield self.rich_log_handler.console  # type: ignore


class DruidHelper(App):
    CSS_PATH = "layout.tcss"

    def __init__(self, rich_log_handler: RichHandler, *args, **kwargs):
        self.body = Body(rich_log_handler, id="body")
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.body
        yield Footer()

    def on_mount(self) -> None:
        logger.info("asdfasdfasdf")


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
