from objectManager import ObjectTypeEnum
from object import Object

class Point(Object):
	def __init__(self, name: String, x: Float, y: Float):
		super().__init__(self, POINT, name)
		self.x = x
		self.y = y