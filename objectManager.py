from object Import Object
from enum import Enum

class ObjectTypeEnum(Enum):
	POINT = 0
	LINE = 1
	POLYGON = 2

#2D Window and Viewport starts with 0 as all coordinates default values.
window = (0.0, 0.0, 0.0, 0.0)
viewport = (0.0, 0.0, 0.0, 0.0)

#List of objects.
display_file = []

def set_window(xw_min: Float, yw_min: Float, xw_max: Float, yw_max: Float):
	window = (xw_min, yw_min, xw_max, yw_max)

def set_viewport(xvp_min: Float, yvp_min: Float vxp_max: Float, yvp_max: Float):
	viewport = (xvp_min, yvp_min, xvp_max, yvp_max)






