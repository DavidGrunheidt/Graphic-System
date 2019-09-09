import objectManager
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from objectManager import *

surface = None

x = 10
y = 30

def cgi_init():
    global gtkBuilder, window_widget, drawing_area, surface, object_list

    gtkBuilder = Gtk.Builder()
    gtkBuilder.add_from_file('window.glade')

    window_widget = gtkBuilder.get_object('main_window')
    window_widget.connect('destroy', Gtk.main_quit)

    drawing_area = gtkBuilder.get_object('drawing_area')
    drawing_area.connect('draw', draw_cb)
    drawing_area.connect('configure-event', configure_event_cb)

    object_list = gtkBuilder.get_object('list_objects')

    gtkBuilder.connect_signals(Handler())

    window_widget.show_all()
    Gtk.main()

# Clear the surface, removing the scribbles
def clear_surface():
    global surface
    cr = cairo.Context(surface)
    cr.set_source_rgb(1, 1, 1)
    cr.paint()
    del cr

# Creates the surface
def configure_event_cb(wid, evt):
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
    clear_surface()
    return True

# Redraw the screen from the surface
def draw_cb(wid, cr):
    global surface
    cr.set_source_surface(surface, 0, 0)
    cr.paint()
    return False

def show_error(message: str):
    gtkBuilder.add_from_file('showError.glade')
    errorWindow = gtkBuilder.get_object('window_show_error')
    errorWindow.set_transient_for(dialog_newObj)
    errorWindow.set_modal(True)
    errorLabel = gtkBuilder.get_object('label_error')
    errorLabel.set_text(message)
    errorWindow.show_all()

class Handler:
    # Function that will be called when the ok button is pressed
    def new_obj_clicked(self, widget):
        global dialog_newObj, gtkBuilder
        gtkBuilder.add_from_file('dialogNewObj.glade')
        dialog_newObj = gtkBuilder.get_object('dialog_new_obj')
        dialog_newObj.set_transient_for(window_widget)
        dialog_newObj.set_modal(True)
        gtkBuilder.connect_signals(Handler())
        dialog_newObj.show_all()
    
    def btn_rotateX_toggled(self,btn):
        pass

    def btn_rotateY_toggled(self,btn):
        pass

    def btn_rotateZ_toggled(self,btn):
        pass

    def window_zoomIn_clicked(self,btn):
        pass
        
    def window_zoomOut_clicked(self,btn):
        pass

    def window_moveUp_clicked(self,btn):
        pass

    def window_moveDown_clicked(self,btn):
        pass

    def window_moveRight_clicked(self,btn):
        pass

    def window_moveLeft_clicked(self,btn):
        pass 

    def cofirm_new_obj(self, btn):
        global dialog_newObj, gtkBuilder, object_list
        newObj_coordinates_raw = gtkBuilder.get_object('object_coordinates_entry').get_text()
        newObj_coordinates = newObj_coordinates_raw.split(';')

        object_name = gtkBuilder.get_object('object_name_entry').get_text()

        if (object_name in display_file):
            show_error("Nome já definido, escolha outro nome.")
        else:
            error = False

            coordinates_matrix = []
            index_row = 0
            for triple in newObj_coordinates:
                coordinates = triple.split(',')

                try:
                    coordinates = [float(x) for x in coordinates]
                except ValueError:
                    show_error("Insira coordenadas validas. \n Coordenadas devem todas ser duplas de números inteiros ou decimais.")
                    error = True
                    break

                coordinates_matrix.append([])

                if (len(coordinates) == 2 or len(coordinates) == 3):
                    for coordinate in coordinates:
                        coordinates_matrix[index_row].append(coordinate)

                    if (len(coordinates) == 2):
                        coordinates_matrix[index_row].append(0)

                    index_row += 1
                else:
                    show_error("Coordenadas devem ser duplas ou triplas")
                    error = True
                    break

            if (not error):
                newObj = Object(object_name, coordinates_matrix)
                display_file[object_name] = newObj

                listed_object = gtkBuilder.get_object('generic_object_button').new_with_label(object_name+" ("+newObj.type+")")
                object_list.insert(listed_object, -1)
                object_list.show_all()

                cr = cairo.Context(surface)
                cr.move_to(coordinates_matrix[0][0], coordinates_matrix[0][1])

                if (newObj.isPoint):
                    cr.line_to(coordinates_matrix[0][0]+1, coordinates_matrix[0][1]+1)
                else:
                    index_row = 0
                    index_column = 0
                    for coordinates in coordinates_matrix[1:len(coordinates_matrix)]:
                        cr.line_to(coordinates[0], coordinates[1])
                    #cr.line_to(coordinates_matrix[0][0], coordinates_matrix[0][1])
                    cr.close_path() #Se não puder usar esse usa o de cima pra fechar o poligono.

                cr.stroke()
                window_widget.queue_draw()

                dialog_newObj.hide()

                #For debug purpose
                print("Objeto "+"\""+object_name+"\" ("+newObj.type+") criado nas seguintes coordenadas = "+str(coordinates_matrix)+". Display File com "+str(len(display_file))+" objeto(s)") 


    def cancel_new_obj(self, btn):
        global dialog_new_obj
        dialog_newObj.hide()

    def object_toggled(self, btn):
        pass


