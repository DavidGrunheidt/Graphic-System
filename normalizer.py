import objectManager
import clipper
import numpy as np
import math
from object import Object

def world_to_window_coordinates_transform(my_object: Object) -> list:
    window = objectManager.window
    x_wc = (window["xWinMax"] - window["xWinMin"]) / 2
    y_wc = (window["yWinMax"] - window["yWinMin"]) / 2

    new_coordinates = []
    for cord in my_object.coordinates:
        cord_aux = cord[0:2]
        cord_aux.append(1)
        new_coordinates.append(cord_aux)

    move_vector = [-x_wc, -y_wc]
    move_matrix = np.array([[1, 0, 0], [0, 1, 0], [move_vector[0], move_vector[1], 1]])
    new_coordinates = np.array(new_coordinates).dot(move_matrix)

    v_up_angle = -window["vUpAngle"]
    rotate_matrix = np.array([[math.cos(math.radians(v_up_angle)), -math.sin(math.radians(v_up_angle)), 0],
                              [math.sin(math.radians(v_up_angle)), math.cos(math.radians(v_up_angle)), 0], [0, 0, 1]])
    new_coordinates = new_coordinates.dot(rotate_matrix)

    sx = 1 / (window["xWinMax"] - window["xWinMin"])
    sy = 1 / (window["yWinMax"] - window["yWinMin"])
    scale_matrix = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])

    new_coordinates = new_coordinates.dot(scale_matrix).dot(window["transformations"])

    if my_object.is_bezier:
        n_passos = 60
        # print('\n\n' + str([bezier_aux(t, new_coordinates) for t in np.linspace(0, 1, num=n_passos)]))
        return [bezier_aux(t, new_coordinates) for t in np.linspace(0, 1, num=n_passos)]
    elif my_object.is_bspline:
        n_passos = 60
        return bspline_aux(new_coordinates, n_passos)
    else:
        return new_coordinates.tolist()

def zoom_window(scale: float) -> None:
    window = objectManager.window
    display_file = objectManager.display_file

    scale_matrix = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]])
    window["transformations"] = window["transformations"].dot(scale_matrix)

    for obj in display_file:
        normalized_coordinates = np.array(display_file[obj].normalizedCoordinates).dot(scale_matrix)
        clipper.clipObject(obj, normalized_coordinates)

def move_window(step_x: float, step_y: float) -> None:
    window = objectManager.window
    display_file = objectManager.display_file

    move_matrix = np.array([[1, 0, 0], [0, 1, 0], [step_x, step_y, 1]])
    window["transformations"] = window["transformations"].dot(move_matrix)

    for obj in display_file:
        normalized_coordinates = np.array(display_file[obj].normalizedCoordinates).dot(move_matrix)
        clipper.clipObject(obj, normalized_coordinates)

def rotate_window(rotate_angle: float) -> None:
    window = objectManager.window
    display_file = objectManager.display_file

    window_v_up_angle = window["vUpAngle"]

    window_v_up_angle -= rotate_angle
    if window_v_up_angle <= -360:
        window_v_up_angle += 360
    elif window_v_up_angle >= 360:
        window_v_up_angle -= 360

    window["vUpAngle"] = window_v_up_angle

    for obj in display_file:
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj])
        clipper.clipObject(obj, normalized_coordinates)

def set_window_original_size():
    window = objectManager.window
    display_file = objectManager.display_file

    window["vUpAngle"] = 0.0
    window["transformations"] = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    for obj in display_file:
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj])
        clipper.clipObject(obj, normalized_coordinates)

def bezier_aux(t, coordinates) -> list:
    blend_func = np.array([(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3])
    return blend_func.dot(coordinates)

def bspline_aux(coordinates, passos):
    delta = 1 / passos

    E = np.array([[0, 0, 0, 1], [delta ** 3, delta ** 2, delta, 0], [6 * delta ** 3, 2 * delta ** 2, 0, 0], [6 * delta ** 3, 0, 0, 0]])

    new_coords = []

    for index in range(0, len(coordinates) - 3):
        calculated_coords = forward_differences(coordinates[index:index + 4], passos, E)
        new_coords += calculated_coords

    return new_coords

def forward_differences(coordinates, passos, E):
    bspline_matrix = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0], ]) / 6

    coord_aux_x = bspline_matrix.dot([coord[0] for coord in coordinates])
    coord_aux_y = bspline_matrix.dot([coord[1] for coord in coordinates])

    fx = E.dot(coord_aux_x)
    fy = E.dot(coord_aux_y)

    new_coords = [[fx[0], fy[0], 1]]

    for _ in range(1, passos + 1):
        for k in range(len(fx) - 1):
            fx[k] += fx[k + 1]
            fy[k] += fy[k + 1]

        new_coords.append([fx[0], fy[0], 1])

    return new_coords





