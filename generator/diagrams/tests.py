from loguru import logger

from generator.shared import GenericError

from .definitions import MermaidTargetFormat
from .methods import convert_mermaid_to_format


__all__ = ["perform_test"]


def perform_test(filename: str, target_format: MermaidTargetFormat) -> None:
    """Just a quick exploratory test. This will dissapear with unit tests."""

    logger.info(
        f"Converting '{filename}.mmd' to {target_format.value.upper()} format..."
    )
    result = convert_mermaid_to_format(filename, target_format)

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
            f"Arquivo Mermaid '{filename}'.mmd convertido em '{output_filepath}'"
        )
