import objectManager
import clipper
import numpy as np
import math

def world_to_window_coordinates_transform(world_coordinates: list) -> list:
    window = objectManager.window
    x_wc = (window["xWinMax"] - window["xWinMin"]) / 2
    y_wc = (window["yWinMax"] - window["yWinMin"]) / 2

    new_coordinates = []
    for cord in world_coordinates:
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

    new_coordinates = new_coordinates.dot(scale_matrix)
    return new_coordinates.dot(window["transformations"]).tolist()

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
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj].coordinates)
        clipper.clipObject(obj, normalized_coordinates)

def set_window_original_size():
    window = objectManager.window
    display_file = objectManager.display_file

    window["vUpAngle"] = 0.0
    window["transformations"] = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    for obj in display_file:
        normalized_coordinates = world_to_window_coordinates_transform(display_file[obj].coordinates)
        clipper.clipObject(obj, normalized_coordinates)
