from generator.shared import BaseEnum

__all__ = ["MermaidTargetFormat"]


class MermaidTargetFormat(BaseEnum):
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"
