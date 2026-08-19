"""
spotcolor.py

Professionele Spot Color ondersteuning voor Stans Manager.

Doel:
    - Echte PDF Separation Colors
    - Illustrator compatibel
    - STANS / CUTCONTOUR ondersteuning
    - Overprint ondersteuning
    - Herbruikbare resources

Python:
    3.12+

Benodigd:
    pikepdf
"""

from __future__ import annotations

from dataclasses import dataclass
import re

import pikepdf
from pikepdf import Array
from pikepdf import Dictionary
from pikepdf import Name


DEFAULT_SPOT_NAME: str = "STANS"


@dataclass(slots=True, frozen=True)
class SpotColorResources:
    """
    Verwijzingen naar PDF resources.
    """

    spot_name: str
    colorspace_name: str
    extgstate_name: str


def sanitize_spot_name(
    spot_name: str,
) -> str:
    """
    Maak geldige PDF Spot Color naam.

    Illustrator accepteert probleemloos:

        STANS
        CUTCONTOUR
        DIELINE
    """

    cleaned = re.sub(
        r"[^A-Za-z0-9_-]",
        "",
        spot_name.strip(),
    )

    if not cleaned:
        cleaned = DEFAULT_SPOT_NAME

    return cleaned.upper()


def create_tint_transform(
    pdf: pikepdf.Pdf,
) -> pikepdf.Object:
    """
    Maak FunctionType 2 tint transform.

    100% spot = 100% magenta.

    De CMYK-waarde wordt uitsluitend gebruikt
    als alternatieve kleurweergave.
    """

    function = Dictionary(
        {
            Name("/FunctionType"): 2,
            Name("/Domain"): Array([0, 1]),
            Name("/C0"): Array([0, 0, 0, 0]),
            Name("/C1"): Array([0, 1, 0, 0]),
            Name("/N"): 1,
        }
    )

    return pdf.make_indirect(function)


def create_separation_colorspace(
    pdf: pikepdf.Pdf,
    spot_name: str,
) -> pikepdf.Object:
    """
    Maak echte Separation ColorSpace.

    PDF:

    [
        /Separation
        /STANS
        /DeviceCMYK
        Function
    ]
    """

    spot_name = sanitize_spot_name(
        spot_name
    )

    tint_function = create_tint_transform(
        pdf
    )

    colorspace = Array(
        [
            Name("/Separation"),
            Name(f"/{spot_name}"),
            Name("/DeviceCMYK"),
            tint_function,
        ]
    )

    return pdf.make_indirect(
        colorspace
    )


def create_overprint_gstate(
    pdf: pikepdf.Pdf,
) -> pikepdf.Object:
    """
    Maak overprint ExtGState.
    """

    extgstate = Dictionary(
        {
            Name("/Type"): Name("/ExtGState"),
            Name("/OP"): True,
            Name("/op"): True,
            Name("/OPM"): 1,
        }
    )

    return pdf.make_indirect(
        extgstate
    )


def ensure_spot_resources(
    pdf: pikepdf.Pdf,
    spot_name: str,
) -> SpotColorResources:
    """
    Maak gedeelde PDF-resources.
    """

    spot_name = sanitize_spot_name(
        spot_name
    )

    colorspace_name = (
        f"CS_{spot_name}"
    )

    extgstate_name = (
        f"GS_{spot_name}"
    )

    separation = (
        create_separation_colorspace(
            pdf,
            spot_name,
        )
    )

    overprint = (
        create_overprint_gstate(
            pdf
        )
    )

    for page in pdf.pages:

        if "/Resources" not in page.obj:
            page.obj[
                Name("/Resources")
            ] = Dictionary()

        resources = page.obj[
            "/Resources"
        ]

        if "/ColorSpace" not in resources:
            resources[
                Name("/ColorSpace")
            ] = Dictionary()

        if "/ExtGState" not in resources:
            resources[
                Name("/ExtGState")
            ] = Dictionary()

        resources[
            "/ColorSpace"
        ][
            Name(
                f"/{colorspace_name}"
            )
        ] = separation

        resources[
            "/ExtGState"
        ][
            Name(
                f"/{extgstate_name}"
            )
        ] = overprint

    return SpotColorResources(
        spot_name=spot_name,
        colorspace_name=colorspace_name,
        extgstate_name=extgstate_name,
    )


def build_spot_stroke_commands(
    resources: SpotColorResources,
    tint: float = 1.0,
    line_width: float = 0.25,
) -> str:
    """
    Bouw PDF operators voor echte spotkleur.

    Resultaat:

        q
        /GS_STANS gs
        /CS_STANS CS
        1 SCN
        0.25 w
    """

    if tint < 0:
        tint = 0

    if tint > 1:
        tint = 1

    return (
        "q\n"
        f"/{resources.extgstate_name} gs\n"
        f"/{resources.colorspace_name} CS\n"
        f"{tint:.4f} SCN\n"
        f"{line_width:.4f} w\n"
    )


def build_spot_footer() -> str:
    """
    Sluit een content stream af.
    """

    return (
        "S\n"
        "Q\n"
    )


def add_spotcolor_to_pdf(
    input_pdf: str,
    output_pdf: str,
    spot_name: str = DEFAULT_SPOT_NAME,
) -> None:
    """
    Voeg uitsluitend SpotColor resources toe.

    Nuttig voor testen.
    """

    with pikepdf.open(
        input_pdf
    ) as pdf:

        ensure_spot_resources(
            pdf,
            spot_name,
        )

        pdf.save(
            output_pdf
        )


__all__ = [
    "DEFAULT_SPOT_NAME",
    "SpotColorResources",
    "sanitize_spot_name",
    "create_tint_transform",
    "create_separation_colorspace",
    "create_overprint_gstate",
    "ensure_spot_resources",
    "build_spot_stroke_commands",
    "build_spot_footer",
    "add_spotcolor_to_pdf",
]


if __name__ == "__main__":
    print(
        "spotcolor.py geladen"
    )