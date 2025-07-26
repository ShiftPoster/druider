from textual.app import App, ComposeResult
from textual.widgets import Static

from druid_helper.table import Animals
from textual.widgets import Footer, Header


class HorizontalLayoutExample(App):
    CSS_PATH = "layout.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Static(name="Listing", id="sidebar"):
            yield Animals()
        yield Static(name="Details", id="body", classes="box")
        yield Footer()


if __name__ == "__main__":
    app = HorizontalLayoutExample()
    app.run()
