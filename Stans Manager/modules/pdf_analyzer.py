"""
pdf_analyzer.py

PDF analyse-engine voor Stans Manager.

Verantwoordelijkheden:

- Pagina-analyse
- Spot Color detectie
- Dieline detectie
- PDF Box detectie
- Genereren van analyse-rapporten

Python:
    3.12+

Benodigd:
    PyMuPDF (fitz)
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

import json
from pathlib import Path
import re

from typing import Any

import fitz

from constants import DIELINE_KEYWORDS


# ---------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------


@dataclass(slots=True)
class SpotColorInfo:
    """
    Gevonden Spot Color.
    """

    name: str
    colorspace_type: str
    page_number: int


@dataclass(slots=True)
class TextHit:
    """
    Gevonden stans-gerelateerde tekst.
    """

    keyword: str
    text: str
    bbox: tuple[float, float, float, float]


@dataclass(slots=True)
class PageReport:
    """
    Rapport per pagina.
    """

    page_number: int

    width_pt: float
    height_pt: float

    has_trimbox: bool
    has_artbox: bool
    has_cropbox: bool
    has_mediabox: bool

    text_hits: list[TextHit] = field(
        default_factory=list
    )

    spot_colors: list[SpotColorInfo] = field(
        default_factory=list
    )


@dataclass(slots=True)
class PDFReport:
    """
    Volledig PDF rapport.
    """

    filename: str

    page_count: int

    pages: list[PageReport] = field(
        default_factory=list
    )

    detected_spot_colors: list[
        SpotColorInfo
    ] = field(
        default_factory=list
    )

    detected_dielines: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def _safe_xref_object(
    doc: fitz.Document,
    xref: int,
) -> str:
    """
    Veilige object-uitlezing.
    """

    try:
        return doc.xref_object(
            xref,
            compressed=False,
        )

    except Exception:
        return ""


def _normalize_text(
    text: str,
) -> str:
    """
    Normaliseer tekst.
    """

    return re.sub(
        r"\s+",
        " ",
        text.upper(),
    ).strip()


# ---------------------------------------------------------
# Spot Colors
# ---------------------------------------------------------


def detect_spot_colors(
    doc: fitz.Document,
    page: fitz.Page,
) -> list"""
    Zoek Separation en DeviceN colorspaces.
    """

    found: list[
        SpotColorInfo
    ] = []

    try:

        raw_page = _safe_xref_object(
            doc,
            page.xref,
        )

        resources = re.findall(
            r"/Resources\s+(\d+)\s+0\s+R",
            raw_page,
        )

        visited: set[int] = set()

        for resource in resources:

            xref = int(resource)

            if xref in visited:
                continue

            visited.add(xref)

            obj = _safe_xref_object(
                doc,
                xref,
            )

            separation_matches = re.finditer(
                r"/Separation\s*/([^\s/]+)",
                obj,
                re.IGNORECASE,
            )

            for match in separation_matches:

                found.append(
                    SpotColorInfo(
                        name=match.group(1),
                        colorspace_type="Separation",
                        page_number=page.number + 1,
                    )
                )

            devicen_matches = re.finditer(
                r"/DeviceN\s*\[([^\]]+)\]",
                obj,
                re.IGNORECASE | re.DOTALL,
            )

            for match in devicen_matches:

                names = re.findall(
                    r"/([^\s/]+)",
                    match.group(1),
                )

                for color_name in names:

                    found.append(
                        SpotColorInfo(
                            name=color_name,
                            colorspace_type="DeviceN",
                            page_number=page.number + 1,
                        )
                    )

    except Exception:
        pass

    return found


# ---------------------------------------------------------
# Dieline tekst
# ---------------------------------------------------------


def detect_dieline_text(
    page: fitz.Page,
) -> list"""
    Zoek bekende stanswoorden.
    """

    hits: list[TextHit] = []

    try:

        text_dict = page.get_text(
            "dict"
        )

        for block in text_dict.get(
            "blocks",
            [],
        ):

            if block.get("type") != 0:
                continue

            for line in block.get(
                "lines",
                [],
            ):

                parts: list[str] = []

                for span in line.get(
                    "spans",
                    [],
                ):

                    parts.append(
                        span.get(
                            "text",
                            "",
                        )
                    )

                text = "".join(parts)

                normalized = _normalize_text(
                    text
                )

                for keyword in DIELINE_KEYWORDS:

                    if keyword in normalized:

                        hits.append(
                            TextHit(
                                keyword=keyword,
                                text=text,
                                bbox=tuple(
                                    line.get(
                                        "bbox",
                                        (
                                            0,
                                            0,
                                            0,
                                            0,
                                        ),
                                    )
                                ),
                            )
                        )

    except Exception:
        pass

    return hits


# ---------------------------------------------------------
# Pagina analyse
# ---------------------------------------------------------


def analyze_page(
    doc: fitz.Document,
    page: fitz.Page,
) -> PageReport:
    """
    Analyseer één pagina.
    """

    rect = page.rect

    text_hits = detect_dieline_text(
        page
    )

    spot_colors = detect_spot_colors(
        doc,
        page,
    )

    return PageReport(
        page_number=page.number + 1,
        width_pt=float(rect.width),
        height_pt=float(rect.height),
        has_trimbox=page.trimbox.width > 0,
        has_artbox=page.artbox.width > 0,
        has_cropbox=page.cropbox.width > 0,
        has_mediabox=page.mediabox.width > 0,
        text_hits=text_hits,
        spot_colors=spot_colors,
    )


# ---------------------------------------------------------
# PDF Analyse
# ---------------------------------------------------------


def analyze_pdf(
    pdf_path: str | Path,
) -> PDFReport:
    """
    Hoofdfunctie.
    """

    pdf_path = Path(pdf_path)

    doc = fitz.open(
        str(pdf_path)
    )

    try:

        report = PDFReport(
            filename=pdf_path.name,
            page_count=doc.page_count,
            metadata=dict(
                doc.metadata
            ),
        )

        for page in doc:

            page_report = (
                analyze_page(
                    doc,
                    page,
                )
            )

            report.pages.append(
                page_report
            )

            report.detected_spot_colors.extend(
                page_report.spot_colors
            )

            report.detected_dielines += len(
                page_report.text_hits
            )

        return report

    finally:

        doc.close()


# ---------------------------------------------------------
# Export
# ---------------------------------------------------------


def report_to_dict(
    report: PDFReport,
) -> dict[str, Any]:
    """
    Rapport naar dictionary.
    """

    return asdict(report)


def report_to_json(
    report: PDFReport,
    indent: int = 2,
) -> str:
    """
    Rapport naar JSON.
    """

    return json.dumps(
        report_to_dict(
            report
        ),
        indent=indent,
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------


def main() -> None:
    """
    Commandline entrypoint.
    """

    import argparse

    parser = argparse.ArgumentParser(
        description="PDF Analyzer"
    )

    parser.add_argument(
        "pdf",
        help="PDF bestand",
    )

    args = parser.parse_args()

    report = analyze_pdf(
        args.pdf
    )

    print(
        report_to_json(
            report
        )
    )


if __name__ == "__main__":
    main()