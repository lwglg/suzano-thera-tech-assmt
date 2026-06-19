from enums import Enum
from pathlib import Path

from loguru import logger
from mmdc import MermaidConverter

from src.shared import BaseEnum, GenericError, GenericResult

__all__ = ["main_program"]


class MermaidTargetFormat(BaseEnum):
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"


def parse_mardown_to_pdf() -> GenericResult[str]:
    return GenericResult(result="lalah")


def convert_mermaid_to_svg(
        filename: str,
        target_format: MermaidTargetFormat,
        default_input_dir: str = "resources/diagrams/mmd",
        default_output_dir: str = "resources/diagrams/svg"
    ) -> GenericResult[str]:

    errors: list[GenericError] = []

    if target_format.value not in MermaidTargetFormat.values():
        return GenericResult(errors=GenericError(
                name=FileExistsError.__class__.__name__,
                description=f"Formato de saída '{target_format.value}' não suportado. Opções são: {','.join(MermaidTargetFormat.values())}"
        ))


    input_filepath = Path(default_input_dir).joinpath(f"{filename}.mmd")

    if not Path.exists(input_filepath):
        return GenericResult(errors=GenericError(
            name=FileExistsError.__class__.__name__,
            description=f"Arquivo '{input_filepath}' não existe."
        ))

    mermaid_code: str | None = None

    with open(input_filepath) as mmd:
        # Define your diagram
        mermaid_code = mmd.read()

    if mermaid_code is None:
        return GenericResult(errors=GenericError(
            name=ValueError.__class__.__name__,
            description=f"Arquivo {input_filepath} não contém um diagrama."
        ))

    converter = MermaidConverter()

    format_callable_mux = {
        MermaidTargetFormat.PDF.value: lambda inf, outf: converter.to_pdf(input=inf, output_file=outf),
        MermaidTargetFormat.PNG.value: lambda inf, outf: converter.to_png(input=inf, output_file=outf),
        MermaidTargetFormat.SVG.value: lambda inf, outf: converter.to_svg(input=inf, output_file=outf),
    }

    converter_method = format_callable_mux[target_format.value]
    
    output_filepath = Path(default_output_dir).joinpath(f"file")

    converter.to_svg(mermaid_code, output_file="cool_diagram.svg")


def main_program():
    """Run the main generator program."""

    logger.info("Hello from generator!")
