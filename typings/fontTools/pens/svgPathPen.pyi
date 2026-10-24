from collections.abc import Mapping

from fontTools.pens.basePen import AbstractPen

class SVGPathPen(AbstractPen):
    def __init__(self, glyphSet: Mapping[str, object]) -> None: ...
    def getCommands(self) -> str: ...
