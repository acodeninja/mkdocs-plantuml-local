import logging
from typing import Any
from typing import MutableMapping

# Taken from https://github.com/mkdocs/mkdocs/blob/1.5.3/mkdocs/plugins.py
# TODO: Can be removed when support for 1.4.3 is dropped with the release of 1.6.0


class PrefixedLogger(logging.LoggerAdapter):
    """A logger adapter to prefix log messages."""

    def __init__(self, prefix: str, logger: logging.Logger) -> None:
        """
        Initialize the logger adapter.

        Arguments:
            prefix: The string to insert in front of every message.
            logger: The logger instance.
        """
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
        """
        Process the message.

        Arguments:
            msg: The message:
            kwargs: Remaining arguments.

        Returns:
            The processed message.
        """
        return f"{self.prefix}: {msg}", kwargs


def get_plugin_logger(name: str) -> PrefixedLogger:
    """
    Return a logger for plugins.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs,
            prefixing each message with the plugin package name.

    Example:
        ```python
        from mkdocs.plugins import get_plugin_logger

        log = get_plugin_logger(__name__)
        log.info("My plugin message")
        ```
    """
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return PrefixedLogger(name.split(".", 1)[0], logger)
