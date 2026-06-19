from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

from generator.shared import GenericError, GenericResult


__all__ = ["convert_markdown_to_pdf"]


def convert_markdown_to_pdf(
    filename: str,
    default_input_dir: str = ".",
    default_output_dir: str = "resources/docs/pdf",
) -> GenericResult[str]:
    """Convert a markdown file (.md) into a PDF one (.pdf)."""

    input_filepath = Path(default_input_dir).joinpath(f"{filename}.md")

    if not Path.exists(input_filepath):
        return GenericResult(
            errors=GenericError(
                name=FileExistsError.__class__.__name__,
                description=f"Arquivo '{input_filepath}' não existe.",
            )
        )

    md_content: str | None = None

    # Read your markdown content
    with open(input_filepath, encoding="utf-8") as md:
        md_content = md.read()

    if md_content is None:
        return GenericResult(
            errors=GenericError(
                name=ValueError.__class__.__name__,
                description=f"Arquivo {input_filepath} está vazio.",
            )
        )

    # Initialize the PDF writer
    # pdf = MarkdownPdf(toc_level=2)  # Generates a Table of Contents automatically
    pdf = MarkdownPdf()
    # Add your content as a section and save
    pdf.add_section(Section(md_content))

    output_filepath = Path(default_output_dir)
    output_filepath.mkdir(parents=True, exist_ok=True)
    output_filepath.joinpath(f"{filename}.pdf")

    output_abspath = output_filepath.resolve()

    pdf.save(output_abspath)

    return GenericResult(value=str(output_abspath))
