from enum import Enum

class ObjectTypeEnum(Enum):
	POINT = 0
	LINE = 1
	POLYGON = 2

class Object:
	#An object has (0, 0, 0) as it's default coordinates
	def __init__(self, object_type: ObjectTypeEnum, name: String, x: Double = 0, y: Double = 0, z: Double = 0):
		self.object_type = object_type 
		self.name = name
		self.x = x
		self.y = y
		self.z = z

