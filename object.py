class Object:
	def __init__(self, name: str, coordinates: 'list of [x,y,z] coordinates (matrix)'):
		self.name = name
		self.coordinates = coordinates
		self.isPoint = len(coordinates) == 1
		self.isLine = len(coordinates) == 2
		self.isWireframe = len(coordinates) > 2