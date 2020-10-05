from object import Object
from functools import reduce

import normalizer
import clipper
import numpy as np
import math

# 2D Window and Viewport starts with 0 as all coordinates default values.
window = {
	"xWinMin": 0.0,
	"yWinMin": 0.0,
	"xWinMax": 0.0,
	"yWinMax": 0.0,
	"xDif": 0.0,
	"yDif": 0.0,
	"vUpAngle": 0.0,
	"transformations": np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
}

viewport = {
	"xVpMin": 0.0,
	"yVpMin": 0.0,
	"xVpMax": 0.0,
	"yVpMax": 0.0,
	"xDif": 0.0,
	"yDif": 0.0
}

# List of objects.
display_file: dict = {}

def create_new_object(name: str, coordinates: str, line_color: list) -> Object:
	global display_file, window
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

	new_object = Object(name, coordinates_matrix, line_color)
	display_file[name] = new_object

	normalized_coordinates = normalizer.world_to_window_coordinates_transform(coordinates_matrix)
	clipper.clipObject(name, normalized_coordinates)

	# For debug purpose
	print("Objeto "+"\""+new_object.name+"\" ("+new_object.type+") criado nas seguintes coordenadas = "+str(new_object.coordinates)+".\nDisplay File com "+str(len(display_file))+" objeto(s)")

	return new_object

def change_object(name: str, move_vector: list, scale_factors: list, rotate_rate: float, rotateAroundWorldCenter: bool, rotateAroundPointCenter: bool, pointOfRotation: 'list[float]') -> None:
	global display_file, window
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

	coordinates_aux = []
	for x in coordinates:
		x_aux = x[0:2]
		x_aux.append(1)
		coordinates_aux.append(x_aux)

	new_coordinates = np.array(coordinates_aux).dot(transformation_matrix).tolist()
	display_file[name].set_coordinates(new_coordinates)

	normalized_coordinates = normalizer.world_to_window_coordinates_transform(new_coordinates)
	clipper.clipObject(name, normalized_coordinates)

def viewport_transform(normalized_coordinates: list) -> list:
	global display_file, viewport
	coordinates_on_viewport = []
	index_row = 0

	x_min, y_min = -1, -1
	x_dif, y_dif = 2, 2

	for triple in normalized_coordinates:
		coordinates_on_viewport.append([])

		# xw = triple[0]
		xVp = ((triple[0] - x_min) / x_dif) * viewport["xDif"]

		# yw = triple[1]
		yVp = (1 - ((triple[1] - y_min) / y_dif)) * viewport["yDif"]

		coordinates_on_viewport[index_row].append(xVp)
		coordinates_on_viewport[index_row].append(yVp)

		index_row += 1

	return coordinates_on_viewport

def set_window(x_win_min: float, y_win_min: float, x_win_max: float, y_win_max: float) -> None:
	global window
	window["xWinMin"] = x_win_min
	window["yWinMin"] = y_win_min
	window["xWinMax"] = x_win_max
	window["yWinMax"] = y_win_max
	window["xDif"] = x_win_max - x_win_min
	window["yDif"] = y_win_max - y_win_min

def set_viewport(x_vp_min: float, y_vp_min: float, x_vp_max: float, y_vp_max: float) -> None:
	global viewport
	viewport["xVpMin"] = x_vp_min
	viewport["yVpMin"] = y_vp_min
	viewport["xVpMax"] = x_vp_max
	viewport["yVpMax"] = y_vp_max
	viewport["xDif"] = x_vp_max - x_vp_min
	viewport["yDif"] = y_vp_max - y_vp_min



