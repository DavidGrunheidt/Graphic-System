import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from objectManager import *

zoom_scale = 0.05
move_step = 10

def cgi_init() -> None:
    global gtkBuilder, window_widget, drawing_area, surface, object_list, scale

    surface = None

    gtkBuilder = Gtk.Builder()
    gtkBuilder.add_from_file('window.glade')

    window_widget = gtkBuilder.get_object('main_window')
    window_widget.connect('destroy', Gtk.main_quit)

    drawing_area = gtkBuilder.get_object('drawing_area')
    drawing_area.connect('draw', draw_cb)
    drawing_area.connect('configure-event', configure_event_cb)

    object_list = gtkBuilder.get_object('list_objects')

    scale = gtkBuilder.get_object('label_porcentagem')

    gtkBuilder.connect_signals(Handler())

    window_widget.show_all()
    Gtk.main()

def drawn_object(coordinates: list, isPoint: bool) -> None:
    coordinates_on_viewport = viewport_transform(coordinates)

    cr = cairo.Context(surface)
    cr.move_to(coordinates_on_viewport[0][0], coordinates_on_viewport[0][1])

    if (isPoint):
        cr.line_to(coordinates_on_viewport[0][0]+1, coordinates_on_viewport[0][1]+1)
    else:
        index_row = 0
        index_column = 0
        for coordinates in coordinates_on_viewport[1:len(coordinates_on_viewport)]:
            cr.line_to(coordinates[0], coordinates[1])
        #cr.line_to(coordinates_on_viewport[0][0], coordinates_on_viewport[0][1])
        cr.close_path() #Se não puder usar esse usa o de cima pra fechar o poligono.

    cr.stroke()
    window_widget.queue_draw()

def redraw_all_objects() -> None:
    clear_surface()
    for coordinates in get_display_file():
        drawn_object(coordinates, len(coordinates) == 1)

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

    set_viewport(0, 0, width, height)
    set_window_original_size()

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

class Handler:
    # Function that will be called when the ok button is pressed
    def new_obj_clicked(self, widget) -> None:
        global dialog_newObj

        gtkBuilder.add_from_file('dialogNewObj.glade')

        dialog_newObj = gtkBuilder.get_object('dialog_new_obj')
        dialog_newObj.set_transient_for(window_widget)
        dialog_newObj.set_modal(True)

        gtkBuilder.connect_signals(Handler())

        dialog_newObj.show_all()

    def cofirm_new_obj(self, btn) -> None:
        newObj_coordinates_raw = gtkBuilder.get_object('object_coordinates_entry').get_text()
        newObj_name = gtkBuilder.get_object('newObj_name_entry').get_text()

        if (newObj_name in display_file):
            show_error("Nome já definido, escolha outro nome.", dialog_newObj)
        else:
            newObj = None

            try: 
                newObj = create_new_object(newObj_name, newObj_coordinates_raw)
            except ValueError as e:
                show_error(str(e), dialog_newObj)
                return

            object_list.append_text(newObj.name+" ("+newObj.type+")")
            object_list.show_all()
            drawn_object(newObj.coordinates, newObj.isPoint)

            dialog_newObj.destroy()


    def cancel_new_obj(self, btn) -> None:
        dialog_newObj.destroy()
    
    def btn_rotateX_toggled(self,btn) -> None:
        pass

    def btn_rotateY_toggled(self,btn) -> None:
        pass

    def btn_rotateZ_toggled(self,btn) -> None:
        pass

    def window_zoomIn_clicked(self,btn) -> None:
        scale.set_text(str(float(scale.get_text().replace('%', '')) + (zoom_scale * 100))+'%')
        zoom_window(zoom_scale, "in")
        redraw_all_objects()
        
    def window_zoomOut_clicked(self,btn) -> None:
        scale.set_text(str(float(scale.get_text().replace('%', '')) - (zoom_scale * 100))+'%')
        zoom_window(zoom_scale, "out")
        redraw_all_objects()
        
    def window_moveUp_clicked(self,btn) -> None:
        move_window(move_step, "up")
        redraw_all_objects()

    def window_moveDown_clicked(self,btn) -> None:
        move_window(move_step, "down")
        redraw_all_objects()

    def window_moveRight_clicked(self,btn) -> None:
        move_window(move_step, "left")
        redraw_all_objects()

    def window_moveLeft_clicked(self,btn) -> None:
        move_window(move_step, "right")
        redraw_all_objects()


    def set_window_clicked(self, btn) -> None:
        global dialog_setWindow

        gtkBuilder.add_from_file('setWindowDialog.glade')

        dialog_setWindow = gtkBuilder.get_object('dialog_set_window')
        dialog_setWindow.set_transient_for(window_widget)
        dialog_setWindow.set_modal(True)

        gtkBuilder.connect_signals(Handler())

        dialog_setWindow.show_all()

    def confirm_set_window(self, btn) -> None:
        window_coordinates_raw = gtkBuilder.get_object('window_coordinates_entry').get_text()

        coordinates_list = window_coordinates_raw.split(',')

        if (len(coordinates_list) != 4):
            show_error("Insira todos os valores pedidos!", dialog_setWindow)
        else:
            try:
                set_window(float(coordinates_list[0]), float(coordinates_list[1]), float(coordinates_list[2]), float(coordinates_list[3]))
            except ValueError:
                show_error("Coordenadas devem ser todas do tipo float", dialog_setWindow)
                return 

            redraw_all_objects()
            dialog_setWindow.destroy()

    def cancel_set_window(self, btn) -> None:
        dialog_setWindow.destroy()

    def object_selected(self, user_data) -> None:
        if object_list.get_active() == 0:
            return

        object_selected = object_list.get_active_text()
        # Returns the combo box to default, with no selected text
        object_list.set_active(0)



