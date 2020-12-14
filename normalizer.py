import objectManager
import clipper
import numpy as np
from object import Object
from matrices import translate_matrix_2d, identity_matrix_2d, rotate_matrix_2d, scale_matrix_2d, translate_matrix, rotate_x_matrix, rotate_y_matrix, perspective_matrix

def object_coordinates_projection(coordinates: list, perspective: bool = False) -> list:
    window = objectManager.window

    window_x_center = (window["xWinMax"] - window["xWinMin"]) / 2
    window_y_center = (window["yWinMax"] - window["yWinMin"]) / 2

    window_x_angle = -window["xAngle"]
    window_y_angle = -window["yAngle"]

    focus_distance = window["focusDistance"]
    z_coord = window["zCoord"]

    if perspective:
        z_coord -= focus_distance

    new_coordinates = []
    for triple in coordinates:
        quadruple = triple + [1]
        new_coordinates.append(quadruple)

    # Translate window to origin (here we do the opposite, translating all objects)
    move_matrix = translate_matrix(-window_x_center, -window_y_center, -z_coord)
    new_coordinates = np.array(new_coordinates).dot(move_matrix)

    # Rotating window to be parallel to X and Y axes (again we do the opposite, rotating all objects)
    rotate_matrix = rotate_x_matrix(window_x_angle).dot(rotate_y_matrix(window_y_angle))
    new_coordinates = new_coordinates.dot(rotate_matrix)

    if perspective:
        perspective_coordinates = []
        for triple in new_coordinates[:len(new_coordinates) - 1]:
            x = triple[0]
            y = triple[1]
            z = triple[2]

            xp = x/(z/focus_distance)
            yp = y/(z/focus_distance)

            perspective_coordinates.append([xp, yp])
        # Ignoring Z coordinate
        return perspective_coordinates

    # Ignoring Z coordinate
    return [x[:len(x) - 2].tolist() for x in new_coordinates]

def world_to_window_coordinates_transform(my_object: Object) -> list:
    window = objectManager.window
    x_wc = (window["xWinMax"] - window["xWinMin"]) / 2
    y_wc = (window["yWinMax"] - window["yWinMin"]) / 2

    projected_coords = object_coordinates_projection(my_object.coordinates, perspective = True)

    normalized_coords = []
    for pair in projected_coords:
        normalized_coords.append(pair + [1])

    move_matrix = translate_matrix_2d(-x_wc, -y_wc)
    normalized_coords = np.array(normalized_coords).dot(move_matrix)

    z_angle = -window["zAngle"]
    rotate_matrix = rotate_matrix_2d(z_angle)
    normalized_coords = normalized_coords.dot(rotate_matrix)

    sx = 1 / (window["xWinMax"] - window["xWinMin"])
    sy = 1 / (window["yWinMax"] - window["yWinMin"])

    zoom_matrix = scale_matrix_2d(sx, sy)
    normalized_coords = normalized_coords.dot(zoom_matrix).dot(window["transformations"])

    if my_object.is_bezier:
        return bezier(normalized_coords)
    elif my_object.is_bspline:
        return bspline(normalized_coords)
    else:
        return normalized_coords.tolist()

def zoom_window(scale: float) -> None:
    window = objectManager.window
    display_file = objectManager.display_file

    zoom_matrix = scale_matrix_2d(scale, scale)
    window["transformations"] = window["transformations"].dot(zoom_matrix)

    for obj in display_file:
        normalized_coordinates = np.array(display_file[obj].normalizedCoordinates).dot(zoom_matrix)
        clipper.clipObject(obj, normalized_coordinates)

def move_window(step_x: float, step_y: float) -> None:
    window = objectManager.window
    display_file = objectManager.display_file

    move_matrix = translate_matrix_2d(step_x, step_y)
    window["transformations"] = window["transformations"].dot(move_matrix)

    for obj in display_file:
        normalized_coordinates = np.array(display_file[obj].normalizedCoordinates).dot(move_matrix)
        clipper.clipObject(obj, normalized_coordinates)

def move_window_z_axis(step_z: float) -> None:
    window = objectManager.window
    window["zCoord"] += step_z

    display_file = objectManager.display_file
    for obj in display_file:
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj])
        clipper.clipObject(obj, normalized_coordinates)

def rotate_window(rotate_angle: float, x_axis: bool = False, y_axis: bool = False) -> None:
    def check_angle_interval(final_angle: float) -> float:
        if final_angle <= -360:
            return final_angle + 360
        elif final_angle >= 360:
            return final_angle - 360
        else:
            return final_angle

    window = objectManager.window
    new_angle = window["zAngle"]
    if x_axis:
        new_angle = window["xAngle"]
    elif y_axis:
        new_angle = window["yAngle"]

    new_angle = check_angle_interval(new_angle - rotate_angle)
    if x_axis:
        window["xAngle"] = new_angle
    elif y_axis:
        window["yAngle"] = new_angle
    else:
        window["zAngle"] = new_angle

    display_file = objectManager.display_file
    for obj in display_file:
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj])
        clipper.clipObject(obj, normalized_coordinates)

def set_window_original_size():
    window = objectManager.window
    display_file = objectManager.display_file

    window["xAngle"] = 0.0
    window["yAngle"] = 0.0
    window["zAngle"] = 0.0
    window["transformations"] = identity_matrix_2d

    for obj in display_file:
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj])
        clipper.clipObject(obj, normalized_coordinates)

def bezier(coordinates) -> list:
    len_coordinates = len(coordinates)
    new_coords = []
    n_passos = 60

    for index in range(0, len_coordinates - 3):
        new_coords += [bezier_aux(t, coordinates[index:index+4]) for t in np.linspace(0, 1, num=n_passos)]

    return new_coords


def bezier_aux(t, coordinates) -> list:
    blend_func = np.array([(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3])
    return blend_func.dot(coordinates)

def bspline(coordinates):
    n_passos = 60
    delta = 1 / n_passos

    e_matrix = np.array([
        [0, 0, 0, 1],
        [delta ** 3, delta ** 2, delta, 0],
        [6 * delta ** 3, 2 * delta ** 2, 0, 0],
        [6 * delta ** 3, 0, 0, 0]
    ])

    new_coords = []

    for index in range(0, len(coordinates) - 3):
        calculated_coords = forward_differences(coordinates[index:index + 4], n_passos, e_matrix)
        new_coords += calculated_coords

    return new_coords

def forward_differences(coordinates, passos, e_matrix):
    bspline_matrix = np.array([
        [-1, 3, -3, 1],
        [3, -6, 3, 0],
        [-3, 0, 3, 0],
        [1, 4, 1, 0]
    ]) / 6

    coord_x = bspline_matrix.dot([triple[0] for triple in coordinates])
    coord_y = bspline_matrix.dot([triple[1] for triple in coordinates])

    fx = e_matrix.dot(coord_x)
    fy = e_matrix.dot(coord_y)

    new_coords = [[fx[0], fy[0], 1, 1]]

    for _ in range(1, passos + 1):
        for k in range(len(fx) - 1):
            fx[k] += fx[k + 1]
            fy[k] += fy[k + 1]

        new_coords.append([fx[0], fy[0], 1, 1])

    return new_coords





