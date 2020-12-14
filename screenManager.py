import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from test_objects import create_test_objects

import object
import objectManager
import clipper
import normalizer

surface = None

zoom_scale = 0.8
move_step = 0.1
move_z_step = 10

def cgi_init() -> None:
    global gtkBuilder, window_widget, drawing_area, object_list, scale, change_obj_options

    gtkBuilder = Gtk.Builder()
    gtkBuilder.add_from_file('window.glade')

    change_obj_options = gtkBuilder.get_object('paned_label_change_object')

    window_widget = gtkBuilder.get_object('main_window')
    window_widget.connect('destroy', Gtk.main_quit)

    drawing_area = gtkBuilder.get_object('drawing_area')
    drawing_area.connect('draw', draw_cb)
    drawing_area.connect('configure-event', configure_event_cb)

    object_list = gtkBuilder.get_object('list_objects')

    scale = gtkBuilder.get_object('label_porcentagem')

    gtkBuilder.connect_signals(Handler())

    window_widget.show_all()

    drawn_canvas()

    # Hides object change options (only showed when an object is selected)
    change_obj_options.hide()

    Gtk.main()

def drawn_canvas() -> None:
    canvas_normalized_coordinates = clipper.canvas
    canvas_obj = object.Object('___canvas', list(), [0.7, 0.2, 0], False, False, False)
    canvas_obj.setToDrawnCoordinates(canvas_normalized_coordinates)
    canvas_obj.setOnBorderList([-1, -1, -1, -1])
    canvas_obj.setOnLineList([[0, 1], [0, 1], [1, 2], [1, 2], [2, 3], [2, 3], [3, 0], [3, 0]])
    drawn_object(canvas_obj)

def drawn_object(obj: object.Object) -> None:
    if not obj.toDrawnCoordinates:
        return

    coordinates_on_viewport = objectManager.viewport_transform(obj.toDrawnCoordinates)

    cr = cairo.Context(surface)
    cr.move_to(coordinates_on_viewport[0][0], coordinates_on_viewport[0][1])

    if obj.isPoint:
        cr.line_to(coordinates_on_viewport[0][0]+1, coordinates_on_viewport[0][1]+1)
    else:
        previous_on_border = obj.onBorderList[0]
        last = obj.onLineList[0]
        for index in range(len(coordinates_on_viewport)):
            coord = coordinates_on_viewport[index]
            if obj.is3D:
                cr.move_to(coord[0], coord[1])
                cr.line_to(coord[0]+1, coord[1]+1)
            else:
                if index == 0:
                    cr.move_to(coord[0], coord[1])
                else:
                    test_list = obj.onLineList[index]

                    # Os pontos pertencem a mesma reta ? (Quando clipa pode ter 2 pontos adjacentes na lista que não pertencem a mesma reta.
                    # Se não pertencem, não trace uma reta entre eles.
                    if test_list == last or test_list[0] == last[1]:
                        # Os pontos pertencem a mesma reta mas estão sobre uma mesma borda?
                        # Se sim, não trace uma reta, se não ela ficaria em cima da borda.
                        if previous_on_border in clipper.on_border_enum and obj.onBorderList[
                            index] in clipper.on_border_enum:
                            if previous_on_border == obj.onBorderList[index]:
                                cr.move_to(coord[0], coord[1])
                            else:
                                cr.line_to(coord[0], coord[1])
                            previous_on_border = obj.onBorderList[index]
                        else:
                            cr.line_to(coord[0], coord[1])
                            previous_on_border = obj.onBorderList[index]
                    else:
                        cr.move_to(coord[0], coord[1])

                    last = test_list


        if obj.name == '___canvas':
            clipper.canvas_viewport_coords = coordinates_on_viewport
            cr.close_path()  # Ou -> cr.line_to(coordinates_on_viewport[0][0], coordinates_on_viewport[0][1])

    cr.set_source_rgb(obj.line_color[0], obj.line_color[1], obj.line_color[2])
    cr.stroke()
    window_widget.queue_draw()

def redraw_all_objects() -> None:
    clear_surface()
    drawn_canvas()
    for obj_name in objectManager.display_file:
        obj = objectManager.display_file[obj_name]
        drawn_object(obj)

# Clear the surface, removing the scribbles
def clear_surface() -> None:
    cr = cairo.Context(surface)
    cr.set_source_rgb(1, 1, 1)
    cr.paint()
    del cr
    #Forces surface to update
    window_widget.queue_draw()

# Creates the surface
def configure_event_cb(wid, evt) -> None:
    global surface, width, height

    if surface is not None:
        del surface
        surface = None

    win = wid.get_window()
    width = wid.get_allocated_width()
    height = wid.get_allocated_height()
    surface = win.create_similar_surface(
        cairo.CONTENT_COLOR,
        width,
        height)

    objectManager.set_viewport(0, 0, width, height)
    objectManager.set_window(0, 0, width, height)

    clear_surface()

    return True

# Redraw the screen from the surface
def draw_cb(wid, cr) -> None:
    cr.set_source_surface(surface, 0, 0)
    cr.paint()
    return False

def show_error(message: str, transient_wid) -> None:
    gtkBuilder.add_from_file('showError.glade')

    errorWindow = gtkBuilder.get_object('window_show_error')
    errorWindow.set_transient_for(transient_wid)
    errorWindow.set_modal(True)

    errorLabel = gtkBuilder.get_object('label_error')
    errorLabel.set_text(message)

    errorWindow.show_all()

def show_dialog(file_name: str, window_id) -> None:
    global dialog

    gtkBuilder.add_from_file(file_name)

    dialog = gtkBuilder.get_object(window_id)
    dialog.set_transient_for(window_widget)
    dialog.set_modal(True)

    gtkBuilder.connect_signals(Handler())

    dialog.show_all()

def drawn_test_objects() -> None:
    create_test_objects(object_list, drawn_object)

class Handler:

    # Function that will be called when the ok button is pressed
    def new_obj_clicked(self, widget) -> None:
        show_dialog('dialogNewObj.glade', 'dialog_new_obj')

    def cofirm_new_obj(self, btn) -> None:
        newObj_coordinates_raw = gtkBuilder.get_object('object_coordinates_entry').get_text()
        newObj_name = gtkBuilder.get_object('newObj_name_entry').get_text()

        if newObj_name in objectManager.display_file:
            show_error("Nome já definido, escolha outro nome.", dialog)
        else:
            newObj = None

            line_color_str = gtkBuilder.get_object('combo_box_color_selected').get_active_text()

            rgb = [0, 0, 0]
            if (line_color_str == "Vermelho"):
                rgb = [0.7, 0.2, 0]
            elif (line_color_str == "Verde"):
                rgb = [0.1, 0.8, 0]
            elif (line_color_str == "Azul"):
                rgb = [0.3, 0.4, 0.6]
            elif (line_color_str == "Amarelo"):
                rgb = [0.9, 0.9, 0.007]

            tipo_object = gtkBuilder.get_object('combo_box_tipo_selected').get_active_text()
            is_bezier = False
            is_bspline = False
            if tipo_object == 'Curva Bezier':
                is_bezier = True
            elif tipo_object == 'Curva BSpline':
                is_bspline = True

            try:
                newObj = objectManager.create_new_object(newObj_name, newObj_coordinates_raw, rgb, is_bezier, is_bspline, '3D' in newObj_name)
            except ValueError as e:
                return show_error(str(e), dialog)

            object_list.append_text(newObj.name+" ("+newObj.type+")")
            object_list.show_all()
            drawn_object(newObj)

            dialog.destroy()

    def btn_rotateX_toggled(self,btn) -> None:
        pass

    def btn_rotateY_toggled(self,btn) -> None:
        pass

    def btn_rotateZ_toggled(self,btn) -> None:
        pass

    def window_zoomIn_clicked(self,btn) -> None:
        if float(scale.get_text().replace('%', '')) > 500:
            return show_error("Escala não pode ser maior que 400%", window_widget)

        scale.set_text(str(float(scale.get_text().replace('%', '')) + ((1 - zoom_scale) * 100))+'%')
        normalizer.zoom_window(1/zoom_scale)
        redraw_all_objects()

    def window_zoomOut_clicked(self,btn) -> None:
        if float(scale.get_text().replace('%', '')) < 40:
            return show_error("Escala não pode ser menor que 40%", window_widget)

        scale.set_text(str(float(scale.get_text().replace('%', '')) - ((1 - zoom_scale) * 100))+'%')
        normalizer.zoom_window(zoom_scale)
        redraw_all_objects()

    def window_moveUp_clicked(self,btn) -> None:
        normalizer.move_window(0, -move_step)
        redraw_all_objects()

    def window_moveDown_clicked(self,btn) -> None:
        normalizer.move_window(0, move_step)
        redraw_all_objects()

    def window_moveRight_clicked(self,btn) -> None:
        normalizer.move_window(-move_step, 0)
        redraw_all_objects()

    def window_moveLeft_clicked(self,btn) -> None:
        normalizer.move_window(move_step, 0)
        redraw_all_objects()

    def window_move_forward_clicked(self,btn) -> None:
        normalizer.move_window_z_axis(-move_z_step)
        redraw_all_objects()

    def window_move_backward_clicked(self,btn) -> None:
        normalizer.move_window_z_axis(move_z_step)
        redraw_all_objects()

    def window_rotate_x_clicked(sel, btn) -> None:
        rotate_angle = float(gtkBuilder.get_object('window_rotation_rate_entry').get_text())
        normalizer.rotate_window(rotate_angle, x_axis = True)
        redraw_all_objects()

    def window_rotate_y_clicked(sel, btn) -> None:
        rotate_angle = float(gtkBuilder.get_object('window_rotation_rate_entry').get_text())
        normalizer.rotate_window(rotate_angle, y_axis = True)
        redraw_all_objects()

    def window_rotate_z_clicked(sel, btn) -> None:
        rotate_angle = float(gtkBuilder.get_object('window_rotation_rate_entry').get_text())
        normalizer.rotate_window(rotate_angle)
        redraw_all_objects()

    def set_window_clicked(self, btn) -> None:
        normalizer.set_window_original_size()
        redraw_all_objects()

    def set_object_selected(self, user_data) -> None:
        global object_selected, objScale, objMove, objRotate, rotate_around_x_axis, rotate_around_y_axis

        objScale = False
        objMove = False
        objRotate = False
        rotate_around_x_axis = False
        rotate_around_y_axis = False

        gtkBuilder.get_object('toggle_object_rotate').set_active(False)
        gtkBuilder.get_object('object_rotate_rate_entry').set_text("")
        gtkBuilder.get_object('button_rotate_around_x_axis').set_active(False)
        gtkBuilder.get_object('button_rotate_around_y_axis').set_active(False)
        gtkBuilder.get_object('button_rotate_around_z_axis').set_active(False)
        gtkBuilder.get_object('point_of_rotation_entry').set_text("")
        gtkBuilder.get_object('toggle_object_move').set_active(False)
        gtkBuilder.get_object('object_move_entry').set_text("")
        gtkBuilder.get_object('toggle_object_scale').set_active(False)
        gtkBuilder.get_object('object_zoom_entry').set_text("")

        if object_list.get_active() == 0:
            object_selected = None
            change_obj_options.hide()
            return

        object_selected = object_list.get_active_text().replace("(Ponto)", "").replace("(Linha)", "").replace("(Wireframe)", "").replace(" ", "").replace("(Bezier)", "").replace("(BSpline)", "")

        change_obj_options.show_all()

        self.toggle_object_rotate(None)

    def obj_change_clicked(self, btn) -> None:
        move_vector = None
        scale_factors = None
        rotate_rate = None

        if (objMove):
            try:
                move_vector = [float(x) for x in gtkBuilder.get_object('object_move_entry').get_text().split(',')]
                if (len(move_vector) != 2):
                    return show_error("Forneça um vetor valido (Dx, Dy)", window_widget)
            except ValueError:
                return show_error("Valores Dx, Dy, Dz do vetor de translação devem ser todos floats", window_widget)

        if (objScale):
            try:
                scale_factors = [float(x) for x in gtkBuilder.get_object('object_zoom_entry').get_text().split(',')]
                if(len(scale_factors) != 2):
                    return show_error("Forneça fatores de escalonamento validos (Sx, Sy, Sz)", window_widget)
                else:
                    for x in scale_factors:
                        if (x <= 0):
                            return show_error("Fator de escalonamento deve ser maior que 0 \n (menor que 1 diminui, maior que 1 aumenta)", window_widget)
            except ValueError:
                return show_error("Fatores Sx, Sy, Sz de escalonamento devem ser todos floats", window_widget)

        if (objRotate):
            try:
                rotate_rate = float(gtkBuilder.get_object('object_rotate_rate_entry').get_text())
            except ValueError:
                return show_error("Angulo de rotação deve ser float", window_widget)

        objectManager.change_object(object_selected, move_vector, scale_factors, rotate_rate, rotate_around_x_axis, rotate_around_y_axis)
        redraw_all_objects()

    def toggle_object_scale(self, btn) -> None:
        global objScale

        if (gtkBuilder.get_object('toggle_object_scale').get_active()):
            objScale = True
        else:
            objScale = False

    def toggle_object_move(self, btn) -> None:
        global objMove

        if (gtkBuilder.get_object('toggle_object_move').get_active()):
            objMove = True
        else:
            objMove = False

    def toggle_object_rotate(self, btn) -> None:
        global objRotate

        rotateIsActive = gtkBuilder.get_object('toggle_object_rotate').get_active()
        if (rotateIsActive):
            objRotate = True
            gtkBuilder.get_object('button_rotate_around_x_axis').show_all()
            gtkBuilder.get_object('button_rotate_around_y_axis').show_all()
            gtkBuilder.get_object('button_rotate_around_z_axis').show_all()
        else:
            objRotate = False
            gtkBuilder.get_object('button_rotate_around_x_axis').hide()
            gtkBuilder.get_object('button_rotate_around_y_axis').hide()
            gtkBuilder.get_object('button_rotate_around_z_axis').hide()
            gtkBuilder.get_object('point_of_rotation_entry').hide()

        gtkBuilder.get_object('button_rotate_around_y_axis').set_active(True)

    def toggle_rotate_around_x_axis(self, btn) -> None:
        global rotate_around_x_axis, rotate_around_y_axis

        if gtkBuilder.get_object('button_rotate_around_x_axis').get_active():
            rotate_around_x_axis = True
            rotate_around_y_axis = False

            gtkBuilder.get_object('button_rotate_around_y_axis').set_active(False)
            gtkBuilder.get_object('button_rotate_around_z_axis').set_active(False)
            gtkBuilder.get_object('point_of_rotation_entry').hide()
        else:
            self.toggle_rotate_around_y_axis(None)

    def toggle_rotate_around_y_axis(self, btn) -> None:
        global rotate_around_x_axis, rotate_around_y_axis

        oneOtherSelected = gtkBuilder.get_object('button_rotate_around_x_axis').get_active() or gtkBuilder.get_object('button_rotate_around_z_axis').get_active()
        thisOneSelected = gtkBuilder.get_object('button_rotate_around_y_axis').get_active()

        if (not oneOtherSelected) or thisOneSelected:
            rotate_around_x_axis = False
            rotate_around_y_axis = True

            gtkBuilder.get_object('button_rotate_around_x_axis').set_active(False)
            gtkBuilder.get_object('button_rotate_around_z_axis').set_active(False)
            gtkBuilder.get_object('point_of_rotation_entry').hide()

            if (not oneOtherSelected):
                gtkBuilder.get_object('button_rotate_around_y_axis').set_active(True)

    def toggle_rotate_around_z_axis(self, btn) -> None:
        global rotate_around_x_axis, rotate_around_y_axis

        if gtkBuilder.get_object('button_rotate_around_z_axis').get_active():
            rotate_around_x_axis = False
            rotate_around_y_axis = False

            gtkBuilder.get_object('button_rotate_around_x_axis').set_active(False)
            gtkBuilder.get_object('button_rotate_around_y_axis').set_active(False)
        else:
            self.toggle_rotate_around_y_axis(None)

    def close_dialog(self, btn) -> None:
        dialog.destroy()

    def button_testar_clicked(self, btn) -> None:
        drawn_test_objects()
        gtkBuilder.get_object('button_testar').hide()



