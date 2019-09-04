from objectManager import ObjectTypeEnum

class Object:
	def __init__(self, object_type: ObjectTypeEnum, name: String):
		self.object_type = object_type 
		self.name = name


