from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Static, Log

from druid_helper.table import Animals


class DruidHelper(App):
    CSS_PATH = "layout.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Static(name="Listing", id="sidebar"):
                yield Animals()
            with Container(name="Details", id="details", classes="box"):
                yield Log()
        yield Footer()


if __name__ == "__main__":
    app = DruidHelper()
    app.run()
