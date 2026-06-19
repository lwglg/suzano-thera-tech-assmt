from generator.diagrams import MermaidTargetFormat, perform_test as perform_mmd2fmt_test
# from generator.markdown import perform_test as perform_md2pdf_test


__all__ = ["main_program"]


def main_program() -> None:
    """Run the main generator program."""

    filename = "arch-diagram-access-mgmt-platform"
    target_format = MermaidTargetFormat.SVG

    perform_mmd2fmt_test(filename, target_format)

    # filename = "all-specs"
    # perform_md2pdf_test(filename)
