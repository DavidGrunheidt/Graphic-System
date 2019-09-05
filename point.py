class Point():
	isPoint = True
	isLine = False
	isPolygon = False

	def __init__(self, name: str, x: float = 0, y: float = 0, z: float = 0) -> None:
		self.name = name
		self.x = x
		self.y = y
		self.z = z
