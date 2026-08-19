"""
logger_manager.py

Centrale logging voor Stans Manager.

Verantwoordelijkheden:

- Logger configureren
- File logging
- Console logging
- Singleton loggerbeheer

Python:
    3.12+

Auteur:
    Ron van der Vlerk
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from constants import DEFAULT_LOG_DIR
from constants import DEFAULT_LOG_FILE


_LOGGERS: dict[str, logging.Logger] = {}


def _create_log_directory() -> Path:
    """
    Maak logmap indien nodig.
    """

    log_dir = Path(
        DEFAULT_LOG_DIR
    )

    log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return log_dir


def _build_formatter() -> logging.Formatter:
    """
    Centrale formatter.
    """

    return logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _add_file_handler(
    logger: logging.Logger,
    log_file: Path,
) -> None:
    """
    Voeg file handler toe.
    """

    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    handler.setLevel(
        logging.INFO
    )

    handler.setFormatter(
        _build_formatter()
    )

    logger.addHandler(
        handler
    )


def _add_console_handler(
    logger: logging.Logger,
) -> None:
    """
    Voeg console handler toe.
    """

    handler = logging.StreamHandler()

    handler.setLevel(
        logging.INFO
    )

    handler.setFormatter(
        _build_formatter()
    )

    logger.addHandler(
        handler
    )


def get_logger(
    name: str = "stans_manager",
) -> logging.Logger:
    """
    Geef geconfigureerde logger terug.

    Voorbeelden:

        logger = get_logger()

        logger = get_logger(
            "stans_manager.processor"
        )

        logger.info("Start")
    """

    if name in _LOGGERS:
        return _LOGGERS[name]

    log_dir = (
        _create_log_directory()
    )

    log_file = log_dir / DEFAULT_LOG_FILE

    logger = logging.getLogger(
        name
    )

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    if not logger.handlers:

        _add_file_handler(
            logger,
            log_file,
        )

        _add_console_handler(
            logger,
        )

    _LOGGERS[name] = logger

    return logger


class ProcessingLogger:
    """
    Legacy compatibiliteitsklasse.

    Oudere code gebruikt:

        ProcessingLogger().logger
    """

    def __init__(
        self,
        name: str = "stans_manager",
    ) -> None:

        self.logger = get_logger(
            name
        )


def shutdown_logging() -> None:
    """
    Sluit alle logginghandlers netjes af.
    """

    for logger in _LOGGERS.values():

        for handler in logger.handlers[:]:

            try:

                handler.flush()

                handler.close()

            finally:

                logger.removeHandler(
                    handler
                )

    _LOGGERS.clear()


__all__ = [
    "get_logger",
    "ProcessingLogger",
    "shutdown_logging",
]


if __name__ == "__main__":

    logger = get_logger(
        "stans_manager.test"
    )

    logger.info(
        "Logger succesvol gestart."
    )

    logger.warning(
        "Test waarschuwing."
    )

    logger.error(
        "Test foutmelding."
    )