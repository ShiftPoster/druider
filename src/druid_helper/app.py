from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Static

from druid_helper.table import Animals


class HorizontalLayoutExample(App):
    CSS_PATH = "layout.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Static(name="Listing", id="sidebar"):
                yield Animals()
            with Container(name="Details", id="details", classes="box"):
                yield Static("This")
                yield Static("panel")
                yield Static("is")
                yield Static("using")
                yield Static("grid layout!", id="bottom-right-final")
        yield Footer()


if __name__ == "__main__":
    app = HorizontalLayoutExample()
    app.run()
