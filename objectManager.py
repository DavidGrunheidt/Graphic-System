from object import Object
from functools import reduce
import numpy as np
import math

#2D Window and Viewport starts with 0 as all coordinates default values.
window = {
	"xWinMin": 0.0, 
	"yWinMin": 0.0, 
	"xWinMax": 0.0, 
	"yWinMax": 0.0,
	"xDif": 0.0,
	"yDif": 0.0,
	"vUpAngle": 0
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

def create_new_object(name: str, coordinates: 'string containing triples of x,y,z coordinates splitted by a ";"', line_color: 'list containing [red, green, blue] amounts') -> Object :
	coordinates_matrix = []
	index_row = 0
	for triple in coordinates.split(';'):
		coordinates = triple.split(',')
		try:
			coordinates = [float(x) for x in coordinates]
		except ValueError:
			raise ValueError("Insira coordenadas validas. \n Coordenadas devem todas ser duplas de números inteiros ou decimais.")

		coordinates_matrix.append([])

		if len(coordinates) == 2 or len(coordinates) == 3:
			for coordinate in coordinates:
				coordinates_matrix[index_row].append(coordinate)

			if len(coordinates) == 2:
				coordinates_matrix[index_row].append(0)

			index_row += 1
		else:
			raise ValueError("Coordenadas devem ser duplas ou triplas")

	newObject = Object(name, coordinates_matrix, line_color)

	display_file[name] = newObject

	#For debug purpose
	print("Objeto "+"\""+newObject.name+"\" ("+newObject.type+") criado nas seguintes coordenadas = "+str(newObject.coordinates)+".\nDisplay File com "+str(len(display_file))+" objeto(s)") 

	return newObject

def change_object(name: str, move_vector: list, scale_factors: list, rotate_rate: float, rotateAroundWorldCenter: bool, rotateAroundPointCenter: bool, pointOfRotation: 'list[float]') -> None:
	move_matrix = np.array([])
	scale_matrix = np.array([])
	rotate_matrix = np.array([])
	transformation_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

	coordinates = display_file[name].coordinates

	cx = reduce(lambda x, y: x + y, [x[0] for x in coordinates])/len(coordinates)
	cy = reduce(lambda x, y: x + y, [x[1] for x in coordinates])/len(coordinates)

	# Obs: Matrix multiplication will be on the order Rotate Matrix * Move Matrix * Scale Matrix always.
	if rotate_rate:
		rotate_matrix = np.array([[math.cos(math.radians(rotate_rate)), -math.sin(math.radians(rotate_rate)), 0], [math.sin(math.radians(rotate_rate)), math.cos(math.radians(rotate_rate)), 0], [0, 0, 1]])
		
		dx = cx
		dy = cy

		if rotateAroundWorldCenter:
			dx = (window["xWinMax"] - window["xWinMin"])/2
			dy = (window["yWinMax"] - window["yWinMin"])/2

		elif rotateAroundPointCenter:
			dx = pointOfRotation[0]
			dy = pointOfRotation[1]

		transformation_matrix = (np.array([[1, 0, 0], [0, 1, 0], [-dx, -dy, 1]]).dot(rotate_matrix)).dot(np.array([[1, 0, 0], [0, 1, 0], [dx, dy, 0]]))

	if move_vector:
		move_matrix = np.array([[1, 0, 0], [0, 1, 0], [move_vector[0], move_vector[1], 1]])
		transformation_matrix = transformation_matrix.dot(move_matrix)

	if scale_factors:
		scale_matrix = np.array([[scale_factors[0], 0, 0], [0, scale_factors[1], 0], [0, 0, 1]])

		transformation_matrix = ((transformation_matrix.dot(np.array([[1, 0, 0], [0, 1, 0], [-cx, -cy, 1]]))).dot(scale_matrix)).dot(np.array([[1, 0, 0], [0, 1, 0], [cx, cy, 1]]))

	coordinatesAux = []
	for x in coordinates:
		xAux = x[0:2]
		xAux.append(1)
		coordinatesAux.append(xAux)

	new_coordinates = np.array(coordinatesAux).dot(transformation_matrix).tolist()

	display_file[name].set_coordinates(new_coordinates)

def world_to_window_coordinates_transform(coordinates) -> list:
	cx = reduce(lambda x, y: x + y, [x[0] for x in coordinates])/len(coordinates)
	cy = reduce(lambda x, y: x + y, [x[1] for x in coordinates])/len(coordinates)

	x_wc = (window["xWinMax"] - window["xWinMin"]) / 2
	y_wc = (window["yWinMax"] - window["yWinMin"]) / 2

	v_up_angle = window["vUpAngle"]
	rotate_matrix = np.array([[math.cos(math.radians(v_up_angle)), -math.sin(math.radians(v_up_angle)), 0], [math.sin(math.radians(v_up_angle)), math.cos(math.radians(v_up_angle)), 0], [0, 0, 1]])
	transformation_matrix = (np.array([[1, 0, 0], [0, 1, 0], [-x_wc, -y_wc, 1]]).dot(rotate_matrix)).dot(np.array([[1, 0, 0], [0, 1, 0], [x_wc, y_wc, 0]]))

	move_vector = [-x_wc, -y_wc]
	move_matrix = np.array([[1, 0, 0], [0, 1, 0], [move_vector[0], move_vector[1], 1]])
	transformation_matrix = transformation_matrix.dot(move_matrix)

	scale_factors = [1, 1]
	scale_matrix = np.array([[scale_factors[0], 0, 0], [0, scale_factors[1], 0], [0, 0, 1]])
	transformation_matrix = ((transformation_matrix.dot(np.array([[1, 0, 0], [0, 1, 0], [-cx, -cy, 1]]))).dot(scale_matrix)).dot(np.array([[1, 0, 0], [0, 1, 0], [cx, cy, 1]]))

	coordinatesAux = []
	for x in coordinates:
		xAux = x[0:2]
		xAux.append(1)
		coordinatesAux.append(xAux)

	return np.array(coordinatesAux).dot(transformation_matrix).tolist()

def viewport_transform(window_coordinates):
	coordinates_on_viewport = []
	index_row = 0

	for triple in window_coordinates:
		coordinates_on_viewport.append([])

		# xw = triple[0]
		xVp = ((triple[0] - window["xWinMin"]) / window["xDif"]) * viewport["xDif"]

		# yw = triple[1]
		yVp = (1 - ((triple[1] - window["yWinMin"]) / window["yDif"])) * viewport["yDif"]

		coordinates_on_viewport[index_row].append(xVp)
		coordinates_on_viewport[index_row].append(yVp)

		index_row += 1

	return coordinates_on_viewport

def zoom_window(scale: float, zoom_type: 'String -> Must be one of this options: in, out') -> None:
	step_x = scale * window["xDif"]
	step_y = scale * window["yDif"] 
	if zoom_type == "out":
		step_x = step_x * -1
		step_y = step_y * -1

	set_window(window["xWinMin"] + step_x, window["yWinMin"] + step_y, window["xWinMax"] - step_x, window["yWinMax"] - step_y)

def move_window(step: float, direction: 'String -> Must be one of this options: left, right, up or down') -> None:
	stepAux = step
	# The if is testing for "down" instead of, intuitively test for "up", because the "y" axis is inverted on the viewport
	# also, we want to move the objects to the inverse of where the window is moving (Window go down -> objects go up)
	if direction == "down" or direction == "right":
		stepAux *= -1

	if direction == "down" or direction == "up":
		window["yWinMin"] += stepAux
		window["yWinMax"] += stepAux
	else:
		window["xWinMin"] += stepAux
		window["xWinMax"] += stepAux

def set_window_original_size():
	global window
	set_window(xWinMin=viewport["xVpMin"], yWinMin=viewport["yVpMin"], xWinMax=viewport["xVpMax"], yWinMax=viewport["yVpMax"])
	set_window_angle(0)

def set_window(xWinMin: float, yWinMin: float, xWinMax: float, yWinMax: float) -> None:
	global window
	window["xWinMin"] = xWinMin
	window["yWinMin"] = yWinMin
	window["xWinMax"] = xWinMax
	window["yWinMax"] = yWinMax
	window["xDif"] = xWinMax - xWinMin
	window["yDif"] = yWinMax - yWinMin

def set_window_angle(rotate_angle: float) -> None:
	global window
	window["vUpAngle"] = rotate_angle

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
	return list(display_file.values())




