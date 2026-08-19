"""
geometry.py

Geometrische hulpmiddelen voor Stans Manager.

Verantwoordelijkheden:
- Omzetten van millimeters naar PDF-punten
- Genereren van PDF path operators
- Ondersteuning voor:
    * Rechthoek
    * Afgeronde rechthoek
    * Cirkel

Python:
    3.12+

Auteur:
    Ron van der Vlerk / OpenAI
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


MM_TO_PT: Final[float] = 72.0 / 25.4
KAPPA: Final[float] = 0.5522847498


@dataclass(frozen=True, slots=True)
class Point:
    """
    Punt in PDF-coördinaten (punten).
    """

    x: float
    y: float


def mm_to_pt(value_mm: float) -> float:
    """
    Converteer millimeters naar PDF-punten.
    """

    if not isinstance(value_mm, (int, float)):
        raise TypeError(
            "value_mm moet een numerieke waarde zijn."
        )

    return float(value_mm) * MM_TO_PT


def pt_to_mm(value_pt: float) -> float:
    """
    Converteer PDF-punten naar millimeters.
    """

    if not isinstance(value_pt, (int, float)):
        raise TypeError(
            "value_pt moet een numerieke waarde zijn."
        )

    return float(value_pt) / MM_TO_PT


def _fmt(value: float) -> str:
    """
    PDF-getal formatteren.
    """

    return (
        f"{value:.6f}"
        .rstrip("0")
        .rstrip(".")
    )


def _validate_dimension(
    value: float,
    name: str,
) -> None:
    """
    Controleer positieve afmetingen.
    """

    if value <= 0:
        raise ValueError(
            f"{name} moet groter zijn dan 0."
        )


def _validate_radius(
    radius_mm: float,
    width_mm: float,
    height_mm: float,
) -> None:
    """
    Controleert de radius.
    """

    if radius_mm < 0:
        raise ValueError(
            "radius_mm mag niet negatief zijn."
        )

    max_radius = min(
        width_mm,
        height_mm,
    ) / 2.0

    if radius_mm > max_radius:
        raise ValueError(
            f"radius_mm mag niet groter zijn dan "
            f"{max_radius:.3f} mm."
        )


def create_rectangle(
    center_x_mm: float,
    center_y_mm: float,
    width_mm: float,
    height_mm: float,
) -> str:
    """
    PDF rectangle operator.

    Retourneert:
        'x y w h re'
    """

    _validate_dimension(
        width_mm,
        "width_mm",
    )

    _validate_dimension(
        height_mm,
        "height_mm",
    )

    width_pt = mm_to_pt(width_mm)
    height_pt = mm_to_pt(height_mm)

    cx_pt = mm_to_pt(center_x_mm)
    cy_pt = mm_to_pt(center_y_mm)

    left = cx_pt - (width_pt / 2.0)
    bottom = cy_pt - (height_pt / 2.0)

    return (
        f"{_fmt(left)} "
        f"{_fmt(bottom)} "
        f"{_fmt(width_pt)} "
        f"{_fmt(height_pt)} re"
    )


def create_rectangle_path(
    center_x_mm: float,
    center_y_mm: float,
    width_mm: float,
    height_mm: float,
) -> str:
    """
    Alias voor compatibiliteit.
    """

    return create_rectangle(
        center_x_mm,
        center_y_mm,
        width_mm,
        height_mm,
    )


def create_rounded_rectangle(
    center_x_mm: float,
    center_y_mm: float,
    width_mm: float,
    height_mm: float,
    radius_mm: float,
) -> str:
    """
    Maak afgeronde rechthoek.

    Gebruikt cubic Bézier-curves.
    """

    _validate_dimension(
        width_mm,
        "width_mm",
    )

    _validate_dimension(
        height_mm,
        "height_mm",
    )

    _validate_radius(
        radius_mm,
        width_mm,
        height_mm,
    )

    w = mm_to_pt(width_mm)
    h = mm_to_pt(height_mm)

    r = mm_to_pt(radius_mm)

    cx = mm_to_pt(center_x_mm)
    cy = mm_to_pt(center_y_mm)

    left = cx - w / 2.0
    right = cx + w / 2.0

    bottom = cy - h / 2.0
    top = cy + h / 2.0

    k = r * KAPPA

    parts: list[str] = []

    parts.append(
        f"{_fmt(left + r)} {_fmt(top)} m"
    )

    parts.append(
        f"{_fmt(right - r)} {_fmt(top)} l"
    )

    parts.append(
        f"{_fmt(right - r + k)} {_fmt(top)} "
        f"{_fmt(right)} {_fmt(top - r + k)} "
        f"{_fmt(right)} {_fmt(top - r)} c"
    )

    parts.append(
        f"{_fmt(right)} {_fmt(bottom + r)} l"
    )

    parts.append(
        f"{_fmt(right)} {_fmt(bottom + r - k)} "
        f"{_fmt(right - r + k)} {_fmt(bottom)} "
        f"{_fmt(right - r)} {_fmt(bottom)} c"
    )

    parts.append(
        f"{_fmt(left + r)} {_fmt(bottom)} l"
    )

    parts.append(
        f"{_fmt(left + r - k)} {_fmt(bottom)} "
        f"{_fmt(left)} {_fmt(bottom + r - k)} "
        f"{_fmt(left)} {_fmt(bottom + r)} c"
    )

    parts.append(
        f"{_fmt(left)} {_fmt(top - r)} l"
    )

    parts.append(
        f"{_fmt(left)} {_fmt(top - r + k)} "
        f"{_fmt(left + r - k)} {_fmt(top)} "
        f"{_fmt(left + r)} {_fmt(top)} c"
    )

    parts.append("h")

    return "\n".join(parts)


def create_rounded_rectangle_path(
    center_x_mm: float,
    center_y_mm: float,
    width_mm: float,
    height_mm: float,
    radius_mm: float,
) -> str:
    """
    Alias voor compatibiliteit.
    """

    return create_rounded_rectangle(
        center_x_mm,
        center_y_mm,
        width_mm,
        height_mm,
        radius_mm,
    )


def create_circle(
    center_x_mm: float,
    center_y_mm: float,
    diameter_mm: float,
) -> str:
    """
    Maak cirkel via vier cubic Bézier-segmenten.
    """

    _validate_dimension(
        diameter_mm,
        "diameter_mm",
    )

    cx = mm_to_pt(center_x_mm)
    cy = mm_to_pt(center_y_mm)

    radius = (
        mm_to_pt(diameter_mm)
        / 2.0
    )

    k = radius * KAPPA

    parts: list[str] = []

    parts.append(
        f"{_fmt(cx + radius)} {_fmt(cy)} m"
    )

    parts.append(
        f"{_fmt(cx + radius)} {_fmt(cy + k)} "
        f"{_fmt(cx + k)} {_fmt(cy + radius)} "
        f"{_fmt(cx)} {_fmt(cy + radius)} c"
    )

    parts.append(
        f"{_fmt(cx - k)} {_fmt(cy + radius)} "
        f"{_fmt(cx - radius)} {_fmt(cy + k)} "
        f"{_fmt(cx - radius)} {_fmt(cy)} c"
    )

    parts.append(
        f"{_fmt(cx - radius)} {_fmt(cy - k)} "
        f"{_fmt(cx - k)} {_fmt(cy - radius)} "
        f"{_fmt(cx)} {_fmt(cy - radius)} c"
    )

    parts.append(
        f"{_fmt(cx + k)} {_fmt(cy - radius)} "
        f"{_fmt(cx + radius)} {_fmt(cy - k)} "
        f"{_fmt(cx + radius)} {_fmt(cy)} c"
    )

    parts.append("h")

    return "\n".join(parts)


def create_circle_path(
    center_x_mm: float,
    center_y_mm: float,
    diameter_mm: float,
) -> str:
    """
    Alias voor compatibiliteit.
    """

    return create_circle(
        center_x_mm,
        center_y_mm,
        diameter_mm,
    )


__all__ = [
    "Point",
    "MM_TO_PT",
    "KAPPA",
    "mm_to_pt",
    "pt_to_mm",
    "create_rectangle",
    "create_rectangle_path",
    "create_rounded_rectangle",
    "create_rounded_rectangle_path",
    "create_circle",
    "create_circle_path",
]