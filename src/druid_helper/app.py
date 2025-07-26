from textual.app import App, ComposeResult
from textual.widgets import Static

from druid_helper.table import Animals


class HorizontalLayoutExample(App):
    CSS_PATH = "layout.tcss"

    def compose(self) -> ComposeResult:
        with Static(name="Listing", id="sidebar"):
            yield Animals()
        yield Static(name="Details", id="body", classes="box")


if __name__ == "__main__":
    app = HorizontalLayoutExample()
    app.run()
