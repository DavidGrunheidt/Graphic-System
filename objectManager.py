from object import Object

#2D Window and Viewport starts with 0 as all coordinates default values.
window = {
	"xWinMin": 0.0, 
	"yWinMin": 0.0, 
	"xWinMax": 0.0, 
	"yWinMax": 0.0,
	"xDif": 0.0,
	"yDif": 0.0
	}

viewport = {
	"xVpMin": 0.0,
	"yVpMin": 0.0, 
	"xVpMax": 0.0, 
	"yVpMax": 0.0,
	"xDif": 0.0,
	"yDif": 0.0
	}

#List of objects.
display_file: dict = {}

def create_new_object(name: str, coordinates: 'string containing triples of x,y,z coordinates splitted by a ";"') -> Object :
	coordinates_matrix = []
	index_row = 0
	for triple in coordinates.split(';'):
		coordinates = triple.split(',')
		try:
			coordinates = [float(x) for x in coordinates]
		except ValueError:
			raise ValueError("Insira coordenadas validas. \n Coordenadas devem todas ser duplas de números inteiros ou decimais.")

		coordinates_matrix.append([])

		if (len(coordinates) == 2 or len(coordinates) == 3):
			for coordinate in coordinates:
				coordinates_matrix[index_row].append(coordinate)

			if (len(coordinates) == 2):
				coordinates_matrix[index_row].append(0)

			index_row += 1
		else:
			raise ValueError("Coordenadas devem ser duplas ou triplas")

	newObject = Object(name, coordinates_matrix)
	display_file[name] = newObject

	#For debug purpose
	print("Objeto "+"\""+newObject.name+"\" ("+newObject.type+") criado nas seguintes coordenadas = "+str(newObject.coordinates)+".\nDisplay File com "+str(len(display_file))+" objeto(s)") 

	return newObject

def viewport_transform(coordinates):
	coordinates_on_viewport = []
	index_row = 0

	for triple in coordinates:
		coordinates_on_viewport.append([])

		# xw = triple[0]
		xVp = ((triple[0] - window["xWinMin"]) / window["xDif"]) * viewport["xDif"]

		# yw = triple[1]
		yVp = (1 - ((triple[1] - window["yWinMin"]) / window["yDif"])) * viewport["yDif"]

		coordinates_on_viewport[index_row].append(xVp)
		coordinates_on_viewport[index_row].append(yVp)

		index_row += 1

	return coordinates_on_viewport

def zoom_window(zoom_type: 'String -> Must be one of this options: in, out') -> None:
	step_x = 0.02 * window["xDif"]
	step_y = 0.02 * window["yDif"] 
	if (zoom_type == "out"):
		step_x = step_x * -1
		step_y = step_y * -1

	set_window(window["xWinMin"] + step_x, window["yWinMin"] + step_y, window["xWinMax"] - step_x, window["yWinMax"] - step_y)

def move_window(direction: 'String -> Must be one of this options: left, right, up or down') -> None:
	step = 10
	# The if is testing for "down" instead of, intuitively test for "up", because the "y" axis is inverted on the viewport
	# also, we want to move the objects to the inverse of where the window is moving (Window go down -> objects go up)
	if (direction == "down" or direction == "right"): 
		step = -10

	if (direction == "down" or direction == "up"):
		window["yWinMin"] += step
		window["yWinMax"] += step
	else:
		window["xWinMin"] += step
		window["xWinMax"] += step

def set_window_original_size():
	global window
	window["xWinMin"] = viewport["xVpMin"]
	window["yWinMin"] = viewport["yVpMin"]
	window["xWinMax"] = viewport["xVpMax"]
	window["yWinMax"] = viewport["yVpMax"]
	window["xDif"] = viewport["xDif"]
	window["yDif"] = viewport["yDif"]

def set_window(xWinMin: float, yWinMin: float, xWinMax: float, yWinMax: float) -> None:
	global window
	window["xWinMin"] = xWinMin
	window["yWinMin"] = yWinMin
	window["xWinMax"] = xWinMax
	window["yWinMax"] = yWinMax
	window["xDif"] = xWinMax - xWinMin
	window["yDif"] = yWinMax - yWinMin

def set_viewport(xVpMin: float, yVpMin: float, xVpMax: float, yVpMax: float) -> None:
	global viewport
	viewport["xVpMin"] = xVpMin
	viewport["yVpMin"] = yVpMin
	viewport["xVpMax"] = xVpMax
	viewport["yVpMax"] = yVpMax
	viewport["xDif"] = xVpMax - xVpMin
	viewport["yDif"] = yVpMax - yVpMin

def get_window() -> (float, float, float, float):
	return window

def get_viewport() -> (float, float, float, float):
	return viewport

def get_display_file() -> list:
	return [x.coordinates for x in list(display_file.values())]




