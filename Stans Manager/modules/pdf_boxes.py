"""
pdf_boxes.py

PDF Box utilities voor Stans Manager.

Ondersteunt:

- TrimBox
- ArtBox
- CropBox
- MediaBox

Alle functies retourneren PdfBoxInfo
zodat de rest van de applicatie geen directe
afhankelijkheid heeft van fitz.Rect.

Python:
    3.12+

Benodigd:
    PyMuPDF
"""

from __future__ import annotations

from pathlib import Path

import fitz

from models import PdfBoxInfo
from models import PdfBoxType


POINTS_PER_MM: float = 72.0 / 25.4


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def _open_document(
    pdf_path: str | Path,
) -> fitz.Document:
    """
    Open PDF document.
    """

    return fitz.open(str(pdf_path))


def _validate_page_number(
    doc: fitz.Document,
    page_number: int,
) -> None:
    """
    Controleer pagina.
    """

    if page_number < 0:
        raise ValueError(
            "page_number mag niet negatief zijn."
        )

    if page_number >= doc.page_count:
        raise IndexError(
            f"Pagina {page_number} bestaat niet."
        )


def _rect_to_box(
    rect: fitz.Rect,
) -> PdfBoxInfo:
    """
    Converteer fitz.Rect naar PdfBoxInfo.
    """

    return PdfBoxInfo(
        x=float(rect.x0),
        y=float(rect.y0),
        width=float(rect.width),
        height=float(rect.height),
    )


def _get_rect(
    page: fitz.Page,
    box_type: PdfBoxType,
) -> fitz.Rect:
    """
    Lees box uit pagina.
    """

    try:

        match box_type:

            case PdfBoxType.TRIMBOX:

                rect = page.trimbox

                if rect and rect.width > 0:
                    return rect

            case PdfBoxType.ARTBOX:

                rect = page.artbox

                if rect and rect.width > 0:
                    return rect

            case PdfBoxType.CROPBOX:

                rect = page.cropbox

                if rect and rect.width > 0:
                    return rect

            case PdfBoxType.MEDIABOX:

                rect = page.mediabox

                if rect and rect.width > 0:
                    return rect

    except Exception:
        pass

    try:

        rect = page.cropbox

        if rect and rect.width > 0:
            return rect

    except Exception:
        pass

    return page.mediabox


# ---------------------------------------------------------
# Generieke functie
# ---------------------------------------------------------


def get_box(
    pdf_path: str | Path,
    page_number: int,
    box_type: PdfBoxType,
) -> PdfBoxInfo:
    """
    Lees willekeurige PDF box.
    """

    doc = _open_document(pdf_path)

    try:

        _validate_page_number(
            doc,
            page_number,
        )

        page = doc[page_number]

        rect = _get_rect(
            page,
            box_type,
        )

        return _rect_to_box(rect)

    finally:

        doc.close()


# ---------------------------------------------------------
# Specifieke box functies
# ---------------------------------------------------------


def get_trimbox(
    pdf_path: str | Path,
    page_number: int,
) -> PdfBoxInfo:
    """
    Lees TrimBox.
    """

    return get_box(
        pdf_path,
        page_number,
        PdfBoxType.TRIMBOX,
    )


def get_artbox(
    pdf_path: str | Path,
    page_number: int,
) -> PdfBoxInfo:
    """
    Lees ArtBox.
    """

    return get_box(
        pdf_path,
        page_number,
        PdfBoxType.ARTBOX,
    )


def get_cropbox(
    pdf_path: str | Path,
    page_number: int,
) -> PdfBoxInfo:
    """
    Lees CropBox.
    """

    return get_box(
        pdf_path,
        page_number,
        PdfBoxType.CROPBOX,
    )


def get_mediabox(
    pdf_path: str | Path,
    page_number: int,
) -> PdfBoxInfo:
    """
    Lees MediaBox.
    """

    return get_box(
        pdf_path,
        page_number,
        PdfBoxType.MEDIABOX,
    )


# ---------------------------------------------------------
# Referentie box
# ---------------------------------------------------------


def get_reference_box(
    pdf_path: str | Path,
    page_number: int,
    box_type: PdfBoxType,
) -> PdfBoxInfo:
    """
    Centrale API die door processor.py
    gebruikt zal worden.
    """

    return get_box(
        pdf_path,
        page_number,
        box_type,
    )


# ---------------------------------------------------------
# Conversies
# ---------------------------------------------------------


def box_to_dict(
    box: PdfBoxInfo,
) -> dict[str, float]:
    """
    Compatibiliteit met legacy code.
    """

    return {
        "x": box.x,
        "y": box.y,
        "width": box.width,
        "height": box.height,
    }


def box_to_mm(
    box: PdfBoxInfo,
) -> PdfBoxInfo:
    """
    Converteer punten naar millimeters.
    """

    return PdfBoxInfo(
        x=box.x / POINTS_PER_MM,
        y=box.y / POINTS_PER_MM,
        width=box.width / POINTS_PER_MM,
        height=box.height / POINTS_PER_MM,
    )


# ---------------------------------------------------------
# Bulk functies
# ---------------------------------------------------------


def get_all_boxes(
    pdf_path: str | Path,
    box_type: PdfBoxType,
) -> dict[int, PdfBoxInfo]:
    """
    Lees dezelfde box van alle pagina's.
    """

    result: dict[int, PdfBoxInfo] = {}

    doc = _open_document(pdf_path)

    try:

        for page_number in range(
            doc.page_count
        ):

            page = doc[page_number]

            rect = _get_rect(
                page,
                box_type,
            )

            result[page_number] = (
                _rect_to_box(rect)
            )

        return result

    finally:

        doc.close()


__all__ = [
    "POINTS_PER_MM",
    "get_box",
    "get_trimbox",
    "get_artbox",
    "get_cropbox",
    "get_mediabox",
    "get_reference_box",
    "box_to_dict",
    "box_to_mm",
    "get_all_boxes",
]