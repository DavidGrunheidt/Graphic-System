class Object:
	def __init__(self, name: str, coordinates: list, line_color: list, is_bezier: bool, is_bspline: bool):
		self.name = name

		self.coordinates = coordinates

		self.isPoint = len(coordinates) == 1
		self.isLine = len(coordinates) == 2
		self.isWireframe = len(coordinates) > 2

		self.is_bezier = is_bezier
		self.is_bspline = is_bspline

		self.type = "Ponto" if self.isPoint else "Linha" if self.isLine else "Wireframe"
		if self.is_bezier:
			self.type = "Bezier"
		elif self.is_bspline:
			self.type = "BSpline"
		self.line_color = line_color

		self.normalizedCoordinates = list()
		self.toDrawnCoordinates = list()
		self.onBorderList = list()
		self.onLineList = list()

	def set_coordinates(self, new_coordinates: list) -> None:
		self.coordinates = new_coordinates

	def setNormalizedCoordinates(self, normalized_coordinates: list) -> None:
		self.normalizedCoordinates = normalized_coordinates

	def setToDrawnCoordinates(self, to_draw_coordinates: list) -> None:
		self.toDrawnCoordinates = to_draw_coordinates

	def setOnBorderList(self, on_border_list: list) -> None:
		self.onBorderList = on_border_list

	def setOnLineList(self, on_line_list: list) -> None:
		self.onLineList = on_line_list