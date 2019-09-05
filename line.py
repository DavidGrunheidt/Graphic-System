from point import Point

class Line():
	isPoint = False
	isLine = True
	isPolygon = False

	def __init__(self, name: str, p1: Point, p2: Point) -> None:
		self.name = name
		self.p1 = p1
		self.p2 = p2
		