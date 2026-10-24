from fontTools.pens.basePen import AbstractPen

class TransformPen(AbstractPen):
    def __init__(self, outPen: AbstractPen, transformation: tuple[float, float, float, float, float, float]) -> None: ...
