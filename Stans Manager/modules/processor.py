"""
processor.py

Centrale verwerkingslaag voor Stans Manager.

Verantwoordelijkheden:

- PDF analyseren
- Optioneel bestaande stanslijnen verwijderen
- Referentiebox bepalen
- Nieuwe stanslijnen schrijven
- Multipage verwerking
- Verwerkingsresultaat retourneren

Python:
    3.12+

Auteur:
    Ron van der Vlerk
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from constants import OUTPUT_SUFFIX
from constants import PT_TO_MM

from logger_manager import get_logger

from models import (
    PdfProcessingRequest,
    PdfProcessingResult,
    ShapeType,
)

from pdf_analyzer import analyze_pdf
from pdf_boxes import get_reference_box
from pdf_cleanup import cleanup_document
from pdf_writer import PDFWriter


LOGGER = get_logger(
    "stans_manager.processor"
)


class PDFProcessor:
    """
    Centrale workflow-engine.
    """

    def process(
        self,
        request: PdfProcessingRequest,
    ) -> PdfProcessingResult:
        """
        Verwerk een PDF.

        Parameters
        ----------
        request:
            Volledig verwerkingsverzoek.

        Returns
        -------
        PdfProcessingResult
        """

        source_pdf = request.source_pdf

        LOGGER.info(
            "Start verwerking: %s",
            source_pdf,
        )

        if not source_pdf.exists():

            return PdfProcessingResult(
                success=False,
                output_pdf=None,
                page_count=0,
                processed_pages=0,
                message=(
                    f"Bestand niet gevonden: "
                    f"{source_pdf}"
                ),
            )

        try:

            report = analyze_pdf(
                source_pdf
            )

            page_count = report.page_count

            if page_count <= 0:

                return PdfProcessingResult(
                    success=False,
                    output_pdf=None,
                    page_count=0,
                    processed_pages=0,
                    message=(
                        "PDF bevat geen pagina's."
                    ),
                )

            with TemporaryDirectory() as temp_dir:

                temp_dir_path = Path(
                    temp_dir
                )

                working_pdf = (
                    temp_dir_path
                    / "working.pdf"
                )

                # ----------------------------------
                # Cleanup oude stanslijnen
                # ----------------------------------

                if (
                    request.remove_existing_dielines
                ):

                    LOGGER.info(
                        "Cleanup bestaande stanslijnen"
                    )

                    cleanup_result = (
                        cleanup_document(
                            input_pdf=source_pdf,
                            output_pdf=working_pdf,
                        )
                    )

                    if not cleanup_result.success:

                        return PdfProcessingResult(
                            success=False,
                            output_pdf=None,
                            page_count=page_count,
                            processed_pages=0,
                            message=(
                                cleanup_result.message
                            ),
                        )

                else:

                    working_pdf.write_bytes(
                        source_pdf.read_bytes()
                    )

                output_pdf = (
                    source_pdf.with_name(
                        f"{source_pdf.stem}"
                        f"{OUTPUT_SUFFIX}.pdf"
                    )
                )

                processed_pages = 0

                with PDFWriter(
                    source_pdf=working_pdf,
                    output_path=output_pdf,
                    spot_name=request.spot_name,
                    line_width=request.line_width_pt,
                ) as writer:

                    pages = (
                        range(page_count)
                        if request.all_pages
                        else [0]
                    )

                    for page_number in pages:

                        box = (
                            get_reference_box(
                                working_pdf,
                                page_number,
                                request.reference_box,
                            )
                        )

                        # --------------------------
                        # PDF punten → mm
                        # --------------------------

                        box_width_mm = (
                            box.width
                            * PT_TO_MM
                        )

                        box_height_mm = (
                            box.height
                            * PT_TO_MM
                        )

                        center_x_mm = (
                            box.center_x
                            * PT_TO_MM
                        )

                        center_y_mm = (
                            box.center_y
                            * PT_TO_MM
                        )

                        center_x_mm += (
                            request.offset_x_mm
                        )

                        center_y_mm += (
                            request.offset_y_mm
                        )

                        width_mm = (
                            request.width_mm
                        )

                        height_mm = (
                            request.height_mm
                        )

                        diameter_mm = (
                            request.diameter_mm
                        )

                        if request.auto_size:

                            width_mm = box_width_mm
                            height_mm = box_height_mm

                            diameter_mm = min(
                                box_width_mm,
                                box_height_mm,
                            )

                        # --------------------------
                        # Bleed toepassen
                        # --------------------------

                        width_mm += (
                            request.bleed_mm * 2
                        )

                        height_mm += (
                            request.bleed_mm * 2
                        )

                        diameter_mm += (
                            request.bleed_mm * 2
                        )

                        # --------------------------
                        # Shape rendering
                        # --------------------------

                        if (
                            request.shape_type
                            == ShapeType.RECTANGLE
                        ):

                            writer.draw_rectangle(
                                page_number=page_number,
                                center_x_mm=center_x_mm,
                                center_y_mm=center_y_mm,
                                width_mm=width_mm,
                                height_mm=height_mm,
                            )

                        elif (
                            request.shape_type
                            == ShapeType.ROUNDED_RECTANGLE
                        ):

                            writer.draw_rounded_rectangle(
                                page_number=page_number,
                                center_x_mm=center_x_mm,
                                center_y_mm=center_y_mm,
                                width_mm=width_mm,
                                height_mm=height_mm,
                                radius_mm=request.radius_mm,
                            )

                        elif (
                            request.shape_type
                            == ShapeType.CIRCLE
                        ):

                            writer.draw_circle(
                                page_number=page_number,
                                center_x_mm=center_x_mm,
                                center_y_mm=center_y_mm,
                                diameter_mm=diameter_mm,
                            )

                        else:

                            return PdfProcessingResult(
                                success=False,
                                output_pdf=None,
                                page_count=page_count,
                                processed_pages=processed_pages,
                                message=(
                                    f"Ongeldig "
                                    f"shape_type: "
                                    f"{request.shape_type}"
                                ),
                            )

                        processed_pages += 1

                    writer.save()

                LOGGER.info(
                    "Verwerking gereed"
                )

                return PdfProcessingResult(
                    success=True,
                    output_pdf=output_pdf,
                    page_count=page_count,
                    processed_pages=processed_pages,
                    message=(
                        "PDF succesvol verwerkt."
                    ),
                )

        except Exception as exc:

            LOGGER.exception(
                "Verwerking mislukt"
            )

            return PdfProcessingResult(
                success=False,
                output_pdf=None,
                page_count=0,
                processed_pages=0,
                message=str(exc),
            )


def process_pdf(
    request: PdfProcessingRequest,
) -> PdfProcessingResult:
    """
    Convenience wrapper.

    Parameters
    ----------
    request:
        Verwerkingsverzoek.

    Returns
    -------
    PdfProcessingResult
    """

    processor = PDFProcessor()

    return processor.process(
        request
    )


__all__ = [
    "PDFProcessor",
    "process_pdf",
]