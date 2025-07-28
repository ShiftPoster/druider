import logging
from pathlib import Path

from rich.logging import RichHandler

from textual.logging import TextualHandler

from druider.app import LoggingConsole, DruidHelper
from druider.data import load_data


def main():
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
