from object import Object
from functools import reduce
from matrices import identity_matrix, identity_matrix_2d, translate_matrix, rotate_x_matrix, rotate_y_matrix, rotate_z_matrix, scale_matrix

import normalizer
import clipper
import numpy as np

# 2D Window and Viewport starts with 0 as all coordinates default values.
window = {
	"xWinMin": 0.0,
	"yWinMin": 0.0,
	"xWinMax": 0.0,
	"yWinMax": 0.0,
	"xDif": 0.0,
	"yDif": 0.0,
	"zCoord": 0.0,
	"xAngle": 0.0,
	"yAngle": 0.0,
	"zAngle": 0.0,
	"transformations": identity_matrix_2d
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

def create_new_object(name: str, coordinates: str, line_color: list, is_bezier: bool, is_bspline: bool) -> Object:
	global display_file, window
	coordinates_matrix = []
	index_row = 0
	for triple in coordinates.split(';'):
		coordinates = triple.split(',')
		try:
			coordinates = [float(x) for x in coordinates]
		except ValueError:
			raise ValueError("Insira coordenadas validas. \n Coordenadas devem todas ser triplas de números inteiros ou decimais.")

		coordinates_matrix.append([])
		if len(coordinates) == 3:
			for coordinate in coordinates:
				coordinates_matrix[index_row].append(coordinate)
			index_row += 1
		else:
			raise ValueError("Coordenadas devem ser triplas")

	new_object = Object(name, coordinates_matrix, line_color, is_bezier, is_bspline)
	display_file[name] = new_object

	normalized_coordinates = normalizer.world_to_window_coordinates_transform(display_file[name])
	clipper.clipObject(name, normalized_coordinates)

	# For debug purpose
	print("Objeto "+"\""+new_object.name+"\" ("+new_object.type+") criado nas seguintes coordenadas = "+str(new_object.coordinates)+".\nDisplay File com "+str(len(display_file))+" objeto(s)")

	return new_object

def change_object(name: str, move_vector: list, scale_factors: list, rotate_rate: float, rotate_x: bool, rotate_y: bool) -> None:
	global display_file, window
	transformation_matrix = identity_matrix
	coordinates = display_file[name].coordinates

	cx = reduce(lambda x, y: x + y, [x[0] for x in coordinates])/len(coordinates)
	cy = reduce(lambda x, y: x + y, [x[1] for x in coordinates])/len(coordinates)
	cz = reduce(lambda x, y: x + y, [x[2] for x in coordinates])/len(coordinates)

	# Obs: Matrix multiplication will be on the order Rotate Matrix * Move Matrix * Scale Matrix always.
	if rotate_rate:
		dx, dy, dz = cx, cy, cz

		rotate_matrix = rotate_z_matrix(rotate_rate)
		if rotate_x:
			rotate_matrix = rotate_x_matrix(rotate_rate)
		elif rotate_y:
			rotate_matrix = rotate_y_matrix(rotate_rate)

		transformation_matrix = translate_matrix(-dx, -dy, -dz).dot(rotate_matrix).dot(translate_matrix(dx, dy, dz))

	if move_vector:
		move_matrix = translate_matrix(move_vector[0], move_vector[1], 0)
		transformation_matrix = transformation_matrix.dot(move_matrix)

	if scale_factors:
		origin_translate_matrix = translate_matrix(-cx, -cy, -cz)
		zoom_matrix = scale_matrix(scale_factors[0], scale_factors[1], 1)
		back_translate_matrix = translate_matrix(cx, cy, cz)

		transformation_matrix = transformation_matrix.dot(origin_translate_matrix).dot(zoom_matrix).dot(back_translate_matrix)

	coordinates_aux = [triple + [1] for triple in coordinates]
	new_coordinates = np.array(coordinates_aux).dot(transformation_matrix).tolist()
	new_coordinates = [quadruple[:len(quadruple) - 1] for quadruple in new_coordinates]

	display_file[name].set_coordinates(new_coordinates)

	normalized_coordinates = normalizer.world_to_window_coordinates_transform(display_file[name])
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
		x_vp = ((triple[0] - x_min) / x_dif) * viewport["xDif"]

		# yw = triple[1]
		y_vp = (1 - ((triple[1] - y_min) / y_dif)) * viewport["yDif"]

		coordinates_on_viewport[index_row].append(x_vp)
		coordinates_on_viewport[index_row].append(y_vp)

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



