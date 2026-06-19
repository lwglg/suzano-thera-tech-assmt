from loguru import logger

from generator.shared import GenericError

from .methods import convert_markdown_to_pdf


__all__ = ["perform_test"]


def perform_test(filename: str, input_dir: str = "sections") -> None:
    """Just a quick exploratory test. This will dissapear with unit tests."""

    logger.info(f"Convertendo '{filename}.md' para um arquivo PDF...")
    result = convert_markdown_to_pdf(filename, default_input_dir=input_dir)

    output_filepath = result.get("value")
    errors = result.get("errors")

    def error_msg(e: GenericError) -> str:
        return f"{e.get('name')}: {e.get('description')}"

    if errors is not None:
        if isinstance(errors, list):
            for err in errors:
                logger.error(error_msg(err))
        else:
            logger.error(error_msg(errors))

    if output_filepath is not None:
        logger.info(
            f"Arquivo markdown '{filename}'.md convertido em '{output_filepath}'"
        )
