"""
models.py

Datamodellen voor Stans Manager.

Dit bestand bevat uitsluitend dataclasses en
gerelateerde enums die gedeeld worden door de
verschillende modules.

Python:
    3.12+

Auteur:
    Ron van der Vlerk
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ShapeType(StrEnum):
    """
    Ondersteunde stansvormen.
    """

    RECTANGLE = "rectangle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    CIRCLE = "circle"


class PdfBoxType(StrEnum):
    """
    Ondersteunde PDF Box types.
    """

    TRIMBOX = "trimbox"
    ARTBOX = "artbox"
    CROPBOX = "cropbox"
    MEDIABOX = "mediabox"


@dataclass(slots=True, frozen=True)
class PdfBoxInfo:
    """
    Gestandaardiseerde PDF-box.
    """

    x: float
    y: float
    width: float
    height: float

    @property
    def center_x(self) -> float:
        return self.x + (self.width / 2.0)

    @property
    def center_y(self) -> float:
        return self.y + (self.height / 2.0)


@dataclass(slots=True, frozen=True)
class SpotColorDefinition:
    """
    Definitie van een spotkleur.
    """

    name: str
    line_width_pt: float
    tint: float = 1.0


@dataclass(slots=True)
class AppConfig:
    """
    Applicatie-configuratie.
    """

    spot_name: str = "STANS"

    bleed_mm: float = 0.0

    stroke_width_pt: float = 0.25

    offset_x_mm: float = 0.0
    offset_y_mm: float = 0.0

    remove_existing_dielines: bool = True

    box_type: PdfBoxType = PdfBoxType.TRIMBOX


@dataclass(slots=True, frozen=True)
class PdfAnalysisSummary:
    """
    Samenvatting van PDF-analyse.
    """

    filename: str

    page_count: int

    detected_spot_colors: int

    detected_dielines: int

    has_trimbox: bool

    has_artbox: bool

    has_cropbox: bool

    has_mediabox: bool


@dataclass(slots=True, frozen=True)
class PdfProcessingRequest:
    """
    Verzoek voor PDF-verwerking.
    """

    source_pdf: Path

    shape_type: ShapeType

    spot_name: str

    reference_box: PdfBoxType

    all_pages: bool

    auto_size: bool

    bleed_mm: float

    line_width_pt: float

    offset_x_mm: float

    offset_y_mm: float

    remove_existing_dielines: bool

    width_mm: float

    height_mm: float

    radius_mm: float

    diameter_mm: float


@dataclass(slots=True, frozen=True)
class PdfProcessingResult:
    """
    Resultaat van verwerking.
    """

    success: bool

    output_pdf: Path | None

    page_count: int

    processed_pages: int

    message: str


__all__ = [
    "ShapeType",
    "PdfBoxType",
    "PdfBoxInfo",
    "SpotColorDefinition",
    "AppConfig",
    "PdfAnalysisSummary",
    "PdfProcessingRequest",
    "PdfProcessingResult",
]