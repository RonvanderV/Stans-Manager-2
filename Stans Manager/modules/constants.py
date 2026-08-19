"""
constants.py

Centrale constanten voor Stans Manager.

Alle projectbrede waarden worden hier beheerd
zodat duplicatie tussen modules wordt voorkomen.

Python:
    3.12+

Auteur:
    Ron van der Vlerk
"""

from __future__ import annotations

from typing import Final


# ---------------------------------------------------------
# Eenheden
# ---------------------------------------------------------

MM_TO_PT: Final[float] = 72.0 / 25.4

PT_TO_MM: Final[float] = 25.4 / 72.0


# ---------------------------------------------------------
# Stanslijnen
# ---------------------------------------------------------

DEFAULT_SPOT_NAME: Final[str] = "STANS"

SUPPORTED_SPOT_NAMES: Final[tuple[str, ...]] = (
    "STANS",
    "CUTCONTOUR",
)


DEFAULT_LINE_WIDTH_PT: Final[float] = 0.25

DEFAULT_BLEED_MM: Final[float] = 0.0


# ---------------------------------------------------------
# PDF Box Types
# ---------------------------------------------------------

TRIMBOX: Final[str] = "trimbox"

ARTBOX: Final[str] = "artbox"

CROPBOX: Final[str] = "cropbox"

MEDIABOX: Final[str] = "mediabox"

SUPPORTED_BOXES: Final[tuple[str, ...]] = (
    TRIMBOX,
    ARTBOX,
    CROPBOX,
    MEDIABOX,
)


# ---------------------------------------------------------
# Dieline detectie
# ---------------------------------------------------------

DIELINE_KEYWORDS: Final[tuple[str, ...]] = (
    "STANS",
    "DIE",
    "DIELINE",
    "CUT",
    "CUTCONTOUR",
    "CUT CONTOUR",
    "KISSCUT",
    "KISSCUT",
    "CONTOUR",
    "OUTLINE",
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

DEFAULT_LOG_DIR: Final[str] = "LOGS"

DEFAULT_LOG_FILE: Final[str] = "processing.log"


# ---------------------------------------------------------
# Config
# ---------------------------------------------------------

CONFIG_FILENAME: Final[str] = "stans_config.json"


# ---------------------------------------------------------
# Bestandsnamen
# ---------------------------------------------------------

OUTPUT_SUFFIX: Final[str] = "_stans"


# ---------------------------------------------------------
# PDF Rendering
# ---------------------------------------------------------

OVERPRINT_MODE: Final[int] = 1

DEFAULT_SPOT_TINT: Final[float] = 1.0


# ---------------------------------------------------------
# PDF Resource Prefixes
# ---------------------------------------------------------

COLORSPACE_PREFIX: Final[str] = "CS_"

EXTGSTATE_PREFIX: Final[str] = "GS_"


# ---------------------------------------------------------
# Exporteer publieke API
# ---------------------------------------------------------

__all__ = [
    "MM_TO_PT",
    "PT_TO_MM",
    "DEFAULT_SPOT_NAME",
    "SUPPORTED_SPOT_NAMES",
    "DEFAULT_LINE_WIDTH_PT",
    "DEFAULT_BLEED_MM",
    "TRIMBOX",
    "ARTBOX",
    "CROPBOX",
    "MEDIABOX",
    "SUPPORTED_BOXES",
    "DIELINE_KEYWORDS",
    "DEFAULT_LOG_DIR",
    "DEFAULT_LOG_FILE",
    "CONFIG_FILENAME",
    "OUTPUT_SUFFIX",
    "OVERPRINT_MODE",
    "DEFAULT_SPOT_TINT",
    "COLORSPACE_PREFIX",
    "EXTGSTATE_PREFIX",
]