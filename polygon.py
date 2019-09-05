from point import Point

class Polygon():
	isPoint = False
	isLine = False
	isPolygon = True

	def __init__(self, name: str, points: 'list of points') -> None:
		self.name = name
		self.points = points
