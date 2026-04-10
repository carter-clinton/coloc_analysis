import logging
import sys
from typing import Any

try:
    from loguru import logger as _LOGURU_LOGGER  # type: ignore
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    _LOGURU_LOGGER = logging.getLogger("la_multitrait")


def setup_logging(level: str = "INFO") -> Any:
    """
    Configure logging once per script. Falls back to stdlib logging if loguru is unavailable.
    """
    if hasattr(_LOGURU_LOGGER, "remove") and hasattr(_LOGURU_LOGGER, "add"):
        _LOGURU_LOGGER.remove()
        _LOGURU_LOGGER.add(sys.stderr, level=level)
    else:
        _LOGURU_LOGGER.setLevel(getattr(logging, level.upper(), logging.INFO))
    return _LOGURU_LOGGER


def get_logger(level: str = "INFO") -> Any:
    return setup_logging(level)
