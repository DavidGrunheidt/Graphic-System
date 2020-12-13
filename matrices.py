import numpy as np
import math

identity_matrix = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

identity_matrix_2d = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

def translate_matrix(dx: float, dy: float, dz: float) -> np.ndarray:
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [dx, dy, dz, 0],
    ])

def translate_matrix_2d(dx: float, dy: float) -> np.ndarray:
    return np.array([
        [1, 0, 0],
        [0, 1, 0],
        [dx, dy, 1],
    ])

def rotate_x_matrix(angle: float) -> np.ndarray:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))
    return np.array([
        [1, 0, 0, 0],
        [0, cos, -sin, 0],
        [0, sin, cos, 0],
        [0, 0, 0, 1]
    ])

def rotate_y_matrix(angle: float) -> np.ndarray:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))
    return np.array([
        [cos, 0, -sin, 0],
        [0, 1, 0, 0],
        [sin, 0, cos, 0],
        [0, 0, 0, 1]
    ])

def rotate_z_matrix(angle: float) -> np.ndarray:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))
    return np.array([
        [cos, -sin, 0, 0],
        [sin, cos, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])

def rotate_matrix_2d(angle: float) -> np.ndarray:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))
    return np.array([
        [cos, -sin, 0],
        [sin, cos, 0],
        [0, 0, 1],
    ])

def scale_matrix(sx: float, sy: float, sz: float) -> np.ndarray:
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def scale_matrix_2d(sx: float, sy: float, sz: float) -> np.ndarray:
    return np.array([
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1],
    ])