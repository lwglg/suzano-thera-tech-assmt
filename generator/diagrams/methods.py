from pathlib import Path
from collections.abc import Callable

from mmdc import MermaidConverter  # type: ignore[import-untyped]

from generator.shared import GenericError, GenericResult

from .definitions import MermaidTargetFormat

__all__ = ["convert_mermaid_to_format"]


def _get_format_callable(
    converter: MermaidConverter, target_format: MermaidTargetFormat
) -> Callable[[str, Path], bytes | None]:
    format_callable_mux = {
        MermaidTargetFormat.PDF.value: lambda code, outf: converter.to_pdf(
            input=code, output_file=outf
        ),
        MermaidTargetFormat.PNG.value: lambda code, outf: converter.to_png(
            input=code, output_file=outf
        ),
        MermaidTargetFormat.SVG.value: lambda code, outf: converter.to_svg(
            input=code, output_file=outf
        ),
    }

    return format_callable_mux[target_format.value]


def convert_mermaid_to_format(
    filename: str,
    target_format: MermaidTargetFormat,
    default_input_dir: str = "resources/diagrams/mmd",
    default_output_dir: str = "resources/diagrams",
) -> GenericResult[str]:
    """Convert a Mermaid diagram file (.mmdd) into another file with a user-issued format."""

    if target_format.value not in MermaidTargetFormat.values():
        return GenericResult(
            errors=GenericError(
                name=FileExistsError.__class__.__name__,
                description=f"Formato de saída '{target_format.value}' não suportado. Opções são: {','.join(MermaidTargetFormat.values())}",
            )
        )

    input_filepath = Path(default_input_dir).joinpath(f"{filename}.mmd")

    if not Path.exists(input_filepath):
        return GenericResult(
            errors=GenericError(
                name=FileExistsError.__class__.__name__,
                description=f"Arquivo '{input_filepath}' não existe.",
            )
        )

    mermaid_code: str | None = None

    with open(input_filepath) as mmd:
        mermaid_code = mmd.read()

    if mermaid_code is None:
        return GenericResult(
            errors=GenericError(
                name=ValueError.__class__.__name__,
                description=f"Arquivo {input_filepath} não contém um diagrama.",
            )
        )

    converter = MermaidConverter()

    converter_method = _get_format_callable(converter, target_format)

    output_filepath = Path(default_output_dir).joinpath(target_format.value)
    output_filepath.mkdir(parents=True, exist_ok=True)
    output_filepath = output_filepath.joinpath(f"{filename}.{target_format.value}")

    output_abspath = output_filepath.resolve()

    converter_method(mermaid_code, output_abspath)

    return GenericResult(value=str(output_abspath))
