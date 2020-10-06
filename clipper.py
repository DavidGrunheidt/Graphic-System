import objectManager

# [Esquerda Baixo, Direita Baixo, Direita Cima, Esquerda Cima] -> Fecha um quadrado
canvas_aux = 0.93
canvas = [[-canvas_aux, -canvas_aux], [canvas_aux, -canvas_aux], [canvas_aux, canvas_aux], [-canvas_aux, canvas_aux]]
canvas_viewport_coords = list()

inside_window_code = [0, 0, 0, 0]

# 0 = Acima, 1 = Abaixo, 2 = Direita, 3 = Esquerda, 4 = Esq. Topo, 5 = Dir. Topo, 6 = Dir. Baixo, 7 = Esq. Baixo
on_border_enum = [0, 1, 2, 3, 4, 5, 6, 7]

x_esquerda = canvas[0][0]
x_direita = canvas[1][0]
y_topo = canvas[2][1]
y_fundo = canvas[0][1]

def clipObject(obj_name: str, normalized_coordinates: list) -> None:
    objectManager.display_file[obj_name].setNormalizedCoordinates(normalized_coordinates)
    region_codes = calculateRegionCodes(normalized_coordinates)

    to_draw_coordinates = list()
    on_border_list = list()
    on_line_list = list()

    # Test each line to see if it's totally, partially or not inside the window.
    for index in range(len(normalized_coordinates)):
        index0 = index
        index1 = index + 1

        if index1 == len(normalized_coordinates):
            index1 = 0

        region_code0 = region_codes[index0]
        region_code1 = region_codes[index1]

        # 0 = Totally Visible; 1 = Not Visible; 2 = Partially Visible
        line_visibility = 0
        if region_code0 == inside_window_code and region_code1 == inside_window_code:
            line_visibility = 0
        elif [region_code0[i] and region_code1[i] for i in range(len(region_code0))] != inside_window_code:
            line_visibility = 1
        else:
            line_visibility = 2

        norm_coord0 = normalized_coordinates[index0]
        norm_coord1 = normalized_coordinates[index1]

        if line_visibility == 0:
            to_draw_coordinates.append(norm_coord0)
            to_draw_coordinates.append(norm_coord1)
            on_border_list += [-1, -1]

            on_line_list += [[index0, index1], [index0, index1]]
        elif line_visibility == 2:
            line_declive = (norm_coord1[1] - norm_coord0[1]) / (norm_coord1[0] - norm_coord0[0])  # (y2 - y1) / (x2 - x1)

            result0 = calculateIntersection(norm_coord0, region_code0, line_declive)
            to_draw_coord0 = result0['coord']
            border0 = result0['border']

            # Interseccão é fora da window, não é necessário calcular x2 - se uma interseccão for fora a outra também será
            if to_draw_coord0[0] < x_esquerda or to_draw_coord0[0] > x_direita or to_draw_coord0[1] < y_fundo or to_draw_coord0[1] > y_topo:
                continue

            result1 = calculateIntersection(norm_coord1, region_code1, line_declive)
            to_draw_coord1 = result1['coord']
            border1 = result1['border']

            to_draw_coordinates.append(to_draw_coord0)
            to_draw_coordinates.append(to_draw_coord1)

            on_border_list.append(border0)
            on_border_list.append(border1)

            on_line_list += [[index0, index1], [index0, index1]]

    objectManager.display_file[obj_name].setToDrawnCoordinates(to_draw_coordinates)
    objectManager.display_file[obj_name].setOnBorderList(on_border_list)
    objectManager.display_file[obj_name].setOnLineList(on_line_list)

def calculateIntersection(coord: list, region_code: list, line_declive: float) -> dict:
    if region_code == inside_window_code:
        return {'coord': coord, 'border': -1}

    # -1 = Dentro, 0 = Acima, 1 = Abaixo, 2 = Direita, 3 = Esquerda, 4 = Esq. Topo, 5 = Dir. Topo, 6 = Dir. Baixo, 7 = Esq. Baixo
    border = -1

    x = 0
    y = 0

    # Topo
    if region_code[0]:
        x = coord[0] + ((1 / line_declive) * (y_topo - coord[1]))

        # Esquerda Topo
        if region_code[3]:
            y = coord[1] + (line_declive * (x_esquerda - coord[0]))

            if x < x_esquerda and y <= y_topo:
                border = 3
                x = x_esquerda
            elif y > y_topo and x >= x_esquerda:
                border = 0
                y = y_topo
            else:
                border = 4

        # Direita Topo
        elif region_code[2]:
            y = coord[1] + (line_declive * (x_direita - coord[0]))

            if x > x_direita and y <= y_topo:
                border = 2
                x = x_direita
            if y > y_topo and x <= x_direita:
                border = 0
                y = y_topo
            else:
                border = 5
        else:
            border = 0
            y = y_topo

    # Fundo
    elif region_code[1]:
        x = coord[0] + ((1 / line_declive) * (y_fundo - coord[1]))

        # Esquerda Baixo
        if region_code[3]:
            y = coord[1] + (line_declive * (x_esquerda - coord[0]))

            if x < x_esquerda and y >= y_fundo:
                border = 3
                x = x_esquerda
            elif y < y_fundo and x >= x_esquerda:
                border = 1
                y = y_fundo
            else:
                border = 7

        # Direita Baixo
        elif region_code[2]:
            y = coord[1] + (line_declive * (x_direita - coord[0]))

            if x > x_direita and y >= y_fundo:
                border = 2
                x = x_direita
            if y < y_fundo and x <= x_direita:
                border = 1
                y = y_fundo
            else:
                border = 6
        else:
            border = 1
            y = y_fundo

    # Direita
    elif region_code[2]:
        border = 2
        x = x_direita
        y = coord[1] + (line_declive * (x_direita - coord[0]))

    # Esquerda
    elif region_code[3]:
        border = 3
        x = x_esquerda
        y = coord[1] + (line_declive * (x_esquerda - coord[0]))

    return {'coord': [x, y], 'border': border}

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