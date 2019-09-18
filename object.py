class Object:
	def __init__(self, name: str, coordinates: 'list of [x,y,z] coordinates (matrix)'):
		self.name = name
		self.coordinates = coordinates
		self.isPoint = len(coordinates) == 1
		self.isLine = len(coordinates) == 2
		self.isWireframe = len(coordinates) > 2
		self.type = "Ponto" if self.isPoint else "Linha" if self.isLine else "Wireframe"

	def set_coordinates(self, new_coordinates: 'list[list[float]]') -> None:
		self.coordinates = new_coordinates
