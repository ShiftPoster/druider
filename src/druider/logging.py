from __future__ import annotations

from typing import TYPE_CHECKING

from rich.logging import RichHandler
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

if TYPE_CHECKING:
    from loguru import FilterDict, FilterFunction, Record


class DruidLog(RichLog):
    file = False
    console: Widget
    handler: RichHandler

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.handler = RichHandler(
            console=self,  # type: ignore
            show_path=False,
            rich_tracebacks=True,
        )

    def print(self, content):
        self.write(content)


def add_to_stdlib() -> DruidLog:
    import logging

    log = DruidLog()
    root = logging.getLogger()
    root.addHandler(log.handler)
    return log


def add_to_loguru(
    level: str | int = "DEBUG",
    filter: str | FilterFunction | FilterDict | None = None,
    **kwargs,
) -> DruidLog:
    from loguru import logger

    log = DruidLog()
    logger.add(
        log.handler,
        format=lambda _: "{message}",
        backtrace=False,
        level=level,
        filter=filter,
        **kwargs,
    )
    return log


def test():
    import logging

    from textual.app import App
    from textual.containers import Vertical
    from textual.widgets import Button, Label

    class LoggingConsole(RichLog):
        file = False
        console: Widget

    logger = logging.getLogger()
    rich_log_handler = RichHandler(
        console=LoggingConsole(),  # type: ignore
        rich_tracebacks=True,
    )
    logger.addHandler(rich_log_handler)
    logger.setLevel(logging.DEBUG)

    logger = logging.getLogger()
    rich_log_handler2 = RichHandler(
        console=LoggingConsole(),  # type: ignore
        rich_tracebacks=True,
    )
    logger.addHandler(rich_log_handler2)
    logger.setLevel(logging.DEBUG)

    class QuestionApp(App[str]):
        DEFAULT_CSS = """
        #buttons {
            height: 20%;
        }
        Vertical {
            border: round green 50%;
        }
        """

        def compose(self) -> ComposeResult:
            with Vertical(name="Buttons", id="buttons"):
                yield Label("Do you love Textual?")
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no", variant="error")
            with Vertical():
                with Vertical():
                    yield rich_log_handler.console  # type: ignore
                with Vertical():
                    yield rich_log_handler2.console  # type: ignore
                    # yield Placeholder()

        def on_button_pressed(self, event: Button.Pressed) -> None:
            logger.info("Button pressed")
            logger.debug(event)
            if event.button.id == "no":
                try:
                    assert "no" == "yes"
                except AssertionError:
                    logger.exception("Assertion error")

    QuestionApp().run()


def test2():
    import logging

    from textual.app import App
    from textual.containers import Vertical
    from textual.widgets import Button, Label

    logger = logging.getLogger(__name__)

    class LoggingConsole(RichLog):
        file = False
        console: Widget

    class QuestionApp(App[str]):
        DEFAULT_CSS = """
        #buttons {
            height: 20%;
        }
        Vertical {
            border: round green 50%;
        }
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.consoles = []
            logger = logging.getLogger()
            for _ in range(2):
                console = LoggingConsole()
                logger.addHandler(
                    RichHandler(
                        console=console,  # type: ignore
                        rich_tracebacks=True,
                    )
                )
                logger.setLevel(logging.DEBUG)
                self.consoles.append(console)

        def compose(self) -> ComposeResult:
            with Vertical(name="Buttons", id="buttons"):
                yield Label("Do you love Textual?")
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no", variant="error")
            with Vertical():
                for console in self.consoles:
                    with Vertical():
                        yield console

        def on_button_pressed(self, event: Button.Pressed) -> None:
            logger.info("Button pressed")
            logger.debug(event)
            if event.button.id == "no":
                try:
                    assert "no" == "yes"
                except AssertionError:
                    logger.exception("Assertion error")

    QuestionApp().run()


def test3():
    from loguru import logger
    from textual.app import App
    from textual.containers import Vertical
    from textual.widgets import Button, Label

    logger.remove()

    class LoggingConsole(RichLog):
        file = False
        console: Widget

    class QuestionApp(App[str]):
        DEFAULT_CSS = """
        #buttons {
            height: 15%;
        }
        Vertical {
            border: round green 50%;
        }
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.consoles = []
            for _ in range(2):
                console = LoggingConsole()
                logger.add(
                    RichHandler(
                        console=console,  # type: ignore
                        rich_tracebacks=True,
                    ),
                    level="DEBUG",
                    format=lambda _: "{message}",
                    backtrace=False,
                )
                self.consoles.append(console)

        def compose(self) -> ComposeResult:
            with Vertical(name="Buttons", id="buttons"):
                yield Label("Do you love Textual?")
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no", variant="error")
            with Vertical():
                for console in self.consoles:
                    with Vertical():
                        yield console

        def on_button_pressed(self, event: Button.Pressed) -> None:
            logger.info("Button pressed")
            logger.debug(event)
            if event.button.id == "no":
                try:
                    assert "no" == "yes"
                except AssertionError:
                    logger.exception("Assertion error")

    QuestionApp().run()


def test4():
    from enum import IntEnum, auto

    from loguru import logger
    from textual.app import App
    from textual.containers import Vertical
    from textual.widgets import Button, Label

    EXTRA: str = "extra"
    logger.remove()

    def button_filter(record: Record, button: str):
        return record.get(EXTRA, {}).get("button") == button

    class Filters(IntEnum):
        yes = 0
        no = auto()

        def log_filter(self, record: Record):
            return button_filter(record=record, button=self.name)

    class LoggingConsole(RichLog):
        file = False
        console: Widget

    class QuestionApp(App[str]):
        DEFAULT_CSS = """
        #buttons {
            height: 15%;
        }
        Vertical {
            border: round green 50%;
        }
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.consoles = []
            for filt in Filters:
                console = LoggingConsole()
                logger.add(
                    RichHandler(
                        console=console,  # type: ignore
                        show_path=False,
                        rich_tracebacks=True,
                    ),
                    level="DEBUG",
                    format=lambda _: "{message}",
                    backtrace=False,
                    filter=filt.log_filter,
                )
                self.consoles.append(console)

        def compose(self) -> ComposeResult:
            with Vertical(name="Buttons", id="buttons"):
                yield Label("Do you love Textual?")
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no", variant="error")
            with Vertical():
                for console in self.consoles:
                    with Vertical():
                        yield console

        def on_button_pressed(self, event: Button.Pressed) -> None:
            logger.info("Button pressed")
            with logger.contextualize(button=event.button.id):
                logger.debug(event)
                if event.button.id == "no":
                    try:
                        assert "no" == "yes"
                    except AssertionError:
                        logger.exception("Assertion error")

    QuestionApp().run()


def test5():
    from enum import IntEnum, auto

    from loguru import logger
    from textual.app import App
    from textual.containers import Vertical
    from textual.widgets import Button, Label

    EXTRA: str = "extra"
    logger.remove()

    def button_filter(record: Record, button: str):
        return record.get(EXTRA, {}).get("button") == button

    class Filters(IntEnum):
        yes = 0
        no = auto()

        def log_filter(self, record: Record):
            return button_filter(record=record, button=self.name)

    class LoggingConsole(RichLog):
        file = False
        console: Widget

    class NewDruidLog(LoggingConsole):
        handler: RichHandler

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.handler = RichHandler(
                console=self,  # type: ignore
                show_path=False,
                rich_tracebacks=True,
            )

    class QuestionApp(App[str]):
        DEFAULT_CSS = """
        #buttons {
            height: 15%;
        }
        Vertical {
            border: round green 50%;
        }
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.consoles = []
            for filt in Filters:
                log = NewDruidLog()
                logger.add(
                    log.handler,
                    level="DEBUG",
                    format=lambda _: "{message}",
                    backtrace=False,
                    filter=filt.log_filter,
                )
                self.consoles.append(log)

        def compose(self) -> ComposeResult:
            with Vertical(name="Buttons", id="buttons"):
                yield Label("Do you love Textual?")
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no", variant="error")
            with Vertical():
                for console in self.consoles:
                    with Vertical():
                        yield console

        def on_button_pressed(self, event: Button.Pressed) -> None:
            logger.info("Button pressed")
            with logger.contextualize(button=event.button.id):
                logger.debug(event)
                if event.button.id == "no":
                    try:
                        assert "no" == "yes"
                    except AssertionError:
                        logger.exception("Assertion error")

    QuestionApp().run()


if __name__ == "__main__":
    test5()
