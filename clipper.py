import objectManager

# [Esquerda Baixo, Direita Baixo, Direita Cima, Esquerda Cima] -> Fecha um quadrado
canvas_aux = 0.93
canvas = [[-canvas_aux, -canvas_aux], [canvas_aux, -canvas_aux], [canvas_aux, canvas_aux], [-canvas_aux, canvas_aux]]

def clipObject(obj_name: str, normalized_coordinates: list) -> None:
    objectManager.display_file[obj_name].setNormalizedCoordinates(normalized_coordinates)
    region_codes = calculateRegionCodes(normalized_coordinates)

def calculateRegionCodes(normalized_coordinates: list) -> list:
    region_codes = list()
    for index in range(len(normalized_coordinates)):
        region_code = list()
        dot = normalized_coordinates[index]
        x = dot[0]
        y = dot[1]

        if y > canvas[2][1]:  # Yi > Ywtopo ?
            region_code.append(1)
        else:
            region_code.append(0)

        if y < canvas[0][1]:  # Yi < Ywfundo ?
            region_code.append(1)
        else:
            region_code.append(0)

        if x > canvas[1][0]:  # Xi > Xwdir ?
            region_code.append(1)
        else:
            region_code.append(0)

        if x < canvas[0][0]:  # Xi < Xwesq ?
            region_code.append(1)
        else:
            region_code.append(0)

        region_codes.append(region_code)
    return region_codes

def get_canvas_normalized_coordinates() -> list:
    global canvas
    return canvas
