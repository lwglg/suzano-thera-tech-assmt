from generator.diagrams import MermaidTargetFormat, perform_test as perform_mmd2fmt_test


__all__ = ["main_program"]


def main_program() -> None:
    """Run the main generator program."""

    filename = "state-diagram-access-mgmt-platform"
    target_format = MermaidTargetFormat.PDF

    perform_mmd2fmt_test(filename, target_format)
