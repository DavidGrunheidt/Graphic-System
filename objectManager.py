from object import Object

#2D Window and Viewport starts with 0 as all coordinates default values.
window = (0.0, 0.0, 0.0, 0.0)
viewport = (0.0, 0.0, 0.0, 0.0)

#List of objects.
display_file: dict = {}

def set_window(xw_min: float, yw_min: float, xw_max: float, yw_max: float) -> bool:
	window = (xw_min, yw_min, xw_max, yw_max)

def set_viewport(xvp_min: float, yvp_min: float, vxp_max: float, yvp_max: float) -> bool:
	viewport = (xvp_min, yvp_min, xvp_max, yvp_max)

def create_new_object(name: str, coordinates: 'list of [x,y,z] coordinates (matrix)'):
	newObject = Object(name, coordinates)
	display_file[name] = newObject






