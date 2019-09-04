from objectManager import ObjectTypeEnum
from object import Object
from 

class Line(Object):
	def __init__(self, name: String, p1: Point, p2: Point):
		super().__init__(self, LINE, name)
		self.p1 = p1
		self.p2 = p2
		