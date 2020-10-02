class Object:
	def __init__(self, name: str, coordinates: list, line_color: list):
		self.name = name

		self.coordinates = coordinates

		self.isPoint = len(coordinates) == 1
		self.isLine = len(coordinates) == 2
		self.isWireframe = len(coordinates) > 2

		self.type = "Ponto" if self.isPoint else "Linha" if self.isLine else "Wireframe"
		self.line_color = line_color

		self.normalizedCoordinates = list()

		self.isClipped = False
		self.toDrawnCoordinates = list()

	def set_coordinates(self, new_coordinates: list) -> None:
		self.coordinates = new_coordinates

	def setNormalizedCoordinates(self, new_coordinates: list) -> None:
		self.normalizedCoordinates = new_coordinates

