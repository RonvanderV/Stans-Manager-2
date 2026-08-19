"""
pdf_cleanup.py

Verwijderen van bestaande stanslijnen,
spot colors en OCG-structuren uit PDF-bestanden.

Doel:
    - Oude STANS verwijderen
    - Oude CUTCONTOUR verwijderen
    - Separation resources verwijderen
    - DeviceN resources verwijderen
    - OCG layers verwijderen
    - PDF optimaliseren

Python:
    3.12+

Benodigd:
    pikepdf
    pymupdf
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz
import pikepdf
from pikepdf import Dictionary
from pikepdf import Name

from constants import DIELINE_KEYWORDS


# ---------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------


@dataclass(slots=True)
class CleanupResult:
    """
    Resultaat van cleanup.
    """

    success: bool

    processed_pages: int

    removed_colorspaces: int

    removed_layers: int

    output_pdf: Path

    message: str


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def _safe_str(
    value: object,
) -> str:
    """
    Veilige conversie naar string.
    """

    try:
        return str(value)
    except Exception:
        return ""


def _contains_dieline_name(
    text: str,
) -> bool:
    """
    Controleer op bekende stansnamen.
    """

    upper = text.upper()

    return any(
        keyword in upper
        for keyword in DIELINE_KEYWORDS
    )


# ---------------------------------------------------------
# Spot Colors
# ---------------------------------------------------------


def remove_spot_colors(
    pdf: pikepdf.Pdf,
) -> int:
    """
    Verwijder Separation en DeviceN resources.
    """

    removed = 0

    for page in pdf.pages:

        resources = page.get(
            "/Resources"
        )

        if resources is None:
            continue

        color_spaces = resources.get(
            "/ColorSpace"
        )

        if color_spaces is None:
            continue

        remove_keys: list[object] = []

        for key, value in color_spaces.items():

            key_name = _safe_str(
                key
            )

            try:

                if (
                    _contains_dieline_name(
                        key_name
                    )
                ):
                    remove_keys.append(
                        key
                    )
                    continue

                if (
                    isinstance(
                        value,
                        pikepdf.Array,
                    )
                    and len(value) > 0
                ):

                    color_type = _safe_str(
                        value[0]
                    )

                    if color_type in (
                        "/Separation",
                        "/DeviceN",
                    ):
                        remove_keys.append(
                            key
                        )

            except Exception:
                continue

        for key in remove_keys:

            try:

                del color_spaces[key]

                removed += 1

            except Exception:
                pass

    return removed


# ---------------------------------------------------------
# Layers
# ---------------------------------------------------------


def remove_layers(
    pdf: pikepdf.Pdf,
) -> int:
    """
    Verwijder OCG-gerelateerde lagen.
    """

    removed = 0

    root = pdf.Root

    if "/OCProperties" in root:

        try:

            del root["/OCProperties"]

            removed += 1

        except Exception:
            pass

    for page in pdf.pages:

        resources = page.get(
            "/Resources"
        )

        if resources is None:
            continue

        properties = resources.get(
            "/Properties"
        )

        if properties is None:
            continue

        removable: list[object] = []

        for key in properties.keys():

            key_name = _safe_str(
                key
            )

            if _contains_dieline_name(
                key_name
            ):
                removable.append(
                    key
                )

        for key in removable:

            try:

                del properties[key]

                removed += 1

            except Exception:
                pass

    return removed


# ---------------------------------------------------------
# Content Cleanup
# ---------------------------------------------------------


def clean_content_streams(
    pdf_path: Path,
) -> int:
    """
    Rebuild content streams met PyMuPDF.
    """

    page_count = 0

    doc = fitz.open(
        str(pdf_path)
    )

    try:

        page_count = doc.page_count

        for page_number in range(
            doc.page_count
        ):

            page = doc[
                page_number
            ]

            try:

                page.clean_contents()

            except Exception:
                pass

        doc.save(
            str(pdf_path),
            garbage=4,
            clean=True,
            deflate=True,
        )

    finally:

        doc.close()

    return page_count


# ---------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------


def cleanup_document(
    input_pdf: str | Path,
    output_pdf: str | Path,
) -> CleanupResult:
    """
    Volledige PDF cleanup.
    """

    input_pdf = Path(
        input_pdf
    )

    output_pdf = Path(
        output_pdf
    )

    temp_path = output_pdf.with_suffix(
        ".tmp.pdf"
    )

    try:

        with pikepdf.open(
            str(input_pdf)
        ) as pdf:

            removed_colors = (
                remove_spot_colors(
                    pdf
                )
            )

            removed_layers_count = (
                remove_layers(
                    pdf
                )
            )

            pdf.save(
                str(temp_path),
                compress_streams=True,
                object_stream_mode=(
                    pikepdf.ObjectStreamMode.generate
                ),
            )

        processed_pages = (
            clean_content_streams(
                temp_path
            )
        )

        temp_path.replace(
            output_pdf
        )

        return CleanupResult(
            success=True,
            processed_pages=processed_pages,
            removed_colorspaces=removed_colors,
            removed_layers=removed_layers_count,
            output_pdf=output_pdf,
            message="Cleanup voltooid.",
        )

    except Exception as exc:

        return CleanupResult(
            success=False,
            processed_pages=0,
            removed_colorspaces=0,
            removed_layers=0,
            output_pdf=output_pdf,
            message=str(exc),
        )


# ---------------------------------------------------------
# Compatibiliteit
# ---------------------------------------------------------


def cleanup_pdf(
    pdf_path: str | Path,
) -> CleanupResult:
    """
    Cleanup in-place.

    Deze functie houdt compatibiliteit
    met oudere code aan.
    """

    pdf_path = Path(
        pdf_path
    )

    return cleanup_document(
        pdf_path,
        pdf_path,
    )


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------


def main() -> None:
    """
    Commandline interface.
    """

    import argparse

    parser = argparse.ArgumentParser(
        description="PDF Cleanup"
    )

    parser.add_argument(
        "input_pdf"
    )

    parser.add_argument(
        "output_pdf"
    )

    args = parser.parse_args()

    result = cleanup_document(
        args.input_pdf,
        args.output_pdf,
    )

    if not result.success:
        raise SystemExit(
            result.message
        )

    print(
        "Cleanup voltooid:"
    )
    print(
        result
    )


if __name__ == "__main__":
    main()