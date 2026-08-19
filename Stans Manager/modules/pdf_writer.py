"""
pdf_writer.py

Professionele PDF dieline writer voor Stans Manager.

Doel:

- Echte Separation Spot Color
- Illustrator compatibel
- STANS / CUTCONTOUR
- Multipage ondersteuning
- Geen RGB lijnen
- Geen CMYK lijnen

Python:
    3.12+

Benodigd:
    pikepdf

Auteur:
    Ron van der Vlerk
"""

from __future__ import annotations

from pathlib import Path

import pikepdf
from pikepdf import Array
from pikepdf import Dictionary
from pikepdf import Name

from geometry import create_circle
from geometry import create_rectangle
from geometry import create_rounded_rectangle

from spotcolor import (
    SpotColorResources,
    build_spot_footer,
    build_spot_stroke_commands,
    ensure_spot_resources,
)


class PDFWriter:
    """
    Centrale PDF writer.

    Werkt volledig op basis van
    Separation Spot Colors.
    """

    def __init__(
        self,
        source_pdf: str | Path,
        output_path: str | Path,
        spot_name: str = "STANS",
        line_width: float = 0.25,
    ) -> None:

        self.source_pdf = Path(source_pdf)
        self.output_path = Path(output_path)

        self.line_width = float(line_width)

        self.pdf = pikepdf.open(
            str(self.source_pdf)
        )

        self.resources: SpotColorResources = (
            ensure_spot_resources(
                self.pdf,
                spot_name,
            )
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _append_stream(
        self,
        page_number: int,
        content: str,
    ) -> None:
        """
        Voeg stream toe aan pagina.
        """

        if page_number < 0:
            raise ValueError(
                "page_number mag niet negatief zijn."
            )

        if page_number >= len(
            self.pdf.pages
        ):
            raise IndexError(
                f"Pagina bestaat niet: "
                f"{page_number}"
            )

        page = self.pdf.pages[
            page_number
        ]

        stream = self.pdf.make_stream(
            content.encode(
                "utf-8"
            )
        )

        contents = page.obj.get(
            "/Contents"
        )

        if contents is None:

            page.obj[
                Name("/Contents")
            ] = stream

            return

        if isinstance(
            contents,
            Array,
        ):

            contents.append(
                stream
            )

            return

        page.obj[
            Name("/Contents")
        ] = Array(
            [
                contents,
                stream,
            ]
        )

    def _build_stream(
        self,
        pdf_path_data: str,
    ) -> str:
        """
        Bouw volledige Separation stream.
        """

        header = (
            build_spot_stroke_commands(
                self.resources,
                tint=1.0,
                line_width=self.line_width,
            )
        )

        footer = (
            build_spot_footer()
        )

        return (
            header
            + pdf_path_data
            + "\n"
            + footer
        )

    # --------------------------------------------------
    # Rectangle
    # --------------------------------------------------

    def draw_rectangle(
        self,
        page_number: int,
        center_x_mm: float,
        center_y_mm: float,
        width_mm: float,
        height_mm: float,
    ) -> None:
        """
        Teken rechthoek.
        """

        path = create_rectangle(
            center_x_mm,
            center_y_mm,
            width_mm,
            height_mm,
        )

        stream = self._build_stream(
            path
        )

        self._append_stream(
            page_number,
            stream,
        )

    # --------------------------------------------------
    # Rounded Rectangle
    # --------------------------------------------------

    def draw_rounded_rectangle(
        self,
        page_number: int,
        center_x_mm: float,
        center_y_mm: float,
        width_mm: float,
        height_mm: float,
        radius_mm: float,
    ) -> None:
        """
        Teken afgeronde rechthoek.
        """

        path = (
            create_rounded_rectangle(
                center_x_mm,
                center_y_mm,
                width_mm,
                height_mm,
                radius_mm,
            )
        )

        stream = self._build_stream(
            path
        )

        self._append_stream(
            page_number,
            stream,
        )

    # --------------------------------------------------
    # Circle
    # --------------------------------------------------

    def draw_circle(
        self,
        page_number: int,
        center_x_mm: float,
        center_y_mm: float,
        diameter_mm: float,
    ) -> None:
        """
        Teken cirkel.
        """

        path = create_circle(
            center_x_mm,
            center_y_mm,
            diameter_mm,
        )

        stream = self._build_stream(
            path
        )

        self._append_stream(
            page_number,
            stream,
        )

    # --------------------------------------------------
    # Multipage helpers
    # --------------------------------------------------

    def page_count(
        self,
    ) -> int:
        """
        Aantal pagina's.
        """

        return len(
            self.pdf.pages
        )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(
        self,
    ) -> Path:
        """
        Sla PDF op.
        """

        self.pdf.save(
            str(
                self.output_path
            ),
            compress_streams=True,
            object_stream_mode=(
                pikepdf.ObjectStreamMode.generate
            ),
        )

        return self.output_path

    def close(
        self,
    ) -> None:
        """
        Sluit document.
        """

        self.pdf.close()

    def __enter__(
        self,
    ) -> "PDFWriter":

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:

        self.close()


# ------------------------------------------------------
# Legacy compatibiliteit
# ------------------------------------------------------


def run(
    *args,
    **kwargs,
) -> bool:
    """
    Scaffold compatibiliteit.
    """

    return True


# ------------------------------------------------------
# Test
# ------------------------------------------------------

if __name__ == "__main__":

    print(
        "pdf_writer.py geladen"
    )