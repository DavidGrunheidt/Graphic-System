import objectManager
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

surface = None

def cgi_init():
    global gtkBuilder, window_widget, drawing_area

    gtkBuilder = Gtk.Builder()
    gtkBuilder.add_from_file('window.glade')

    window_widget = gtkBuilder.get_object('main_window')
    window_widget.connect('destroy', Gtk.main_quit)

    drawing_area = gtkBuilder.get_object('drawing_area')
    drawing_area.connect('draw', draw_cb)
    drawing_area.connect('configure-event', configure_event_cb)

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
    global surface,width,height
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
    pass

# Redraw the screen from the surface
def draw_cb(wid, cr):
    global surface
    cr.set_source_surface(surface, 0, 0)
    cr.paint()
    cr.move_to(0, height/2)
    cr.line_to(width, height/2)
    cr.move_to(width/2, 0)
    cr.line_to(width/2, height)
    return False

class Handler:
    # Function that will be called when the ok button is pressed
    def btn_newObj_clicked(self, btn):
        cr = cairo.Context(surface)
        cr.move_to(0, height/2)
        cr.line_to(width, height/2)
        cr.move_to(width/2, 0)
        cr.line_to(width/2, height)
        cr.stroke()
        window_widget.queue_draw()
    
    def btn_rotateX_toggled(self,btn):
        pass

    def btn_rotateY_toggled(self,btn):
        pass

    def btn_rotateZ_toggled(self,btn):
        pass

    def btn_zoomIn_clicked(self,btn):
        pass
        
    def btn_zoomOut_clicked(self,btn):
        pass

    def btn_moveUp_clicked(self,btn):
        pass

    def btn_moveDown_clicked(self,btn):
        pass

    def btn_moveRight_clicked(self,btn):
        pass

    def btn_moveLeft_clicked(self,btn):
        pass 
