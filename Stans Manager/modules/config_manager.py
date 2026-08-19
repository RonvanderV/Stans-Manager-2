"""
config_manager.py

Configuratiebeheer voor Stans Manager.

Verantwoordelijkheden:

- JSON-configuratie laden
- JSON-configuratie opslaan
- Valideren
- Standaardwaarden beheren

Python:
    3.12+

Auteur:
    Ron van der Vlerk
"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from constants import CONFIG_FILENAME
from constants import DEFAULT_BLEED_MM
from constants import DEFAULT_LINE_WIDTH_PT
from constants import DEFAULT_SPOT_NAME

from models import AppConfig
from models import PdfBoxType


CONFIG_FILE: Path = Path(
    CONFIG_FILENAME
)


def get_default_config() -> AppConfig:
    """
    Maak standaardconfiguratie.
    """

    return AppConfig(
        spot_name=DEFAULT_SPOT_NAME,
        bleed_mm=DEFAULT_BLEED_MM,
        stroke_width_pt=DEFAULT_LINE_WIDTH_PT,
        offset_x_mm=0.0,
        offset_y_mm=0.0,
        remove_existing_dielines=True,
        box_type=PdfBoxType.TRIMBOX,
    )


def _safe_float(
    value: Any,
    default: float,
) -> float:
    """
    Veilige float conversie.
    """

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def _safe_bool(
    value: Any,
    default: bool,
) -> bool:
    """
    Veilige bool conversie.
    """

    if isinstance(
        value,
        bool,
    ):
        return value

    return default


def _safe_box_type(
    value: Any,
) -> PdfBoxType:
    """
    Converteer naar PdfBoxType.
    """

    try:

        return PdfBoxType(
            str(value).lower()
        )

    except Exception:

        return PdfBoxType.TRIMBOX


def _normalize_config(
    data: dict[str, Any],
) -> AppConfig:
    """
    Normaliseer ruwe configuratie.
    """

    default = get_default_config()

    spot_name = str(
        data.get(
            "spot_name",
            default.spot_name,
        )
    ).strip()

    if not spot_name:
        spot_name = DEFAULT_SPOT_NAME

    return AppConfig(
        spot_name=spot_name.upper(),
        bleed_mm=_safe_float(
            data.get(
                "bleed_mm",
                default.bleed_mm,
            ),
            default.bleed_mm,
        ),
        stroke_width_pt=_safe_float(
            data.get(
                "stroke_width_pt",
                default.stroke_width_pt,
            ),
            default.stroke_width_pt,
        ),
        offset_x_mm=_safe_float(
            data.get(
                "offset_x_mm",
                default.offset_x_mm,
            ),
            default.offset_x_mm,
        ),
        offset_y_mm=_safe_float(
            data.get(
                "offset_y_mm",
                default.offset_y_mm,
            ),
            default.offset_y_mm,
        ),
        remove_existing_dielines=_safe_bool(
            data.get(
                "remove_existing_dielines",
                default.remove_existing_dielines,
            ),
            default.remove_existing_dielines,
        ),
        box_type=_safe_box_type(
            data.get(
                "box_type",
                default.box_type.value,
            )
        ),
    )


def load_config() -> AppConfig:
    """
    Lees configuratie uit JSON.
    """

    if not CONFIG_FILE.exists():

        config = get_default_config()

        save_config(
            config
        )

        return config

    try:

        with CONFIG_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Configuratie is geen dictionary."
            )

        return _normalize_config(
            data
        )

    except Exception:

        config = get_default_config()

        save_config(
            config
        )

        return config


def save_config(
    config: AppConfig,
) -> bool:
    """
    Sla configuratie op.
    """

    try:

        data = asdict(
            config
        )

        data["box_type"] = (
            config.box_type.value
        )

        with CONFIG_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return True

    except Exception:

        return False


def reset_config() -> AppConfig:
    """
    Herstel standaardconfiguratie.
    """

    config = (
        get_default_config()
    )

    if not save_config(
        config
    ):
        raise OSError(
            "Kon configuratie niet opslaan."
        )

    return config


def config_exists() -> bool:
    """
    Bestaat configuratiebestand?
    """

    return CONFIG_FILE.exists()


__all__ = [
    "CONFIG_FILE",
    "get_default_config",
    "load_config",
    "save_config",
    "reset_config",
    "config_exists",
]


if __name__ == "__main__":

    cfg = load_config()

    print(cfg)