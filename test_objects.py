from objectManager import create_new_object

def create_test_objects(object_list, drawn_object) -> None:
    obj1 = red_cube()
    obj2 = green_square()
    obj3 = red_triangle()

    objs = [obj1, obj2, obj3]

    for obj in objs:
        object_list.append_text(obj.name + " (" + obj.type + ")")
        object_list.show_all()
        drawn_object(obj)

def yellow_line():
    return create_new_object(
        name='AmrLine',
        coordinates='300,250,200;450,500,300',
        line_color=[0.9, 0.9, 0.007],
        is_bezier=False,
        is_bspline=False
    )

def red_triangle():
    return create_new_object(
        name='VermTri',
        coordinates='400,150,-50;450,320,-40;500,300,-50',
        line_color=[0.7, 0.2, 0],
        is_bezier=False,
        is_bspline=False
    )

def green_bezier():
    return create_new_object(
        name='VerdBez',
        coordinates='50,250,0;70,260,0;90,350,0;120,200,0',
        line_color=[0.1, 0.8, 0],
        is_bezier=True,
        is_bspline=False)

def blue_bspline():
    return create_new_object(
        name='Az',
        coordinates='0,100,100;50,300,250;180,300,45;250,0,12;350,200,78;450,100,90;500,400,100',
        line_color=[0.3, 0.4, 0.6],
        is_bezier=False,
        is_bspline=True
    )

def yellow_plane():
    return create_new_object(
        name='AmrPlane',
        coordinates='60,100,0;160,100,0;160,300,0;60,300,0',
        line_color=[0.9, 0.9, 0.007],
        is_bezier=False,
        is_bspline=False
    )

def red_cube():
    return create_new_object(
        name='VermCube',
        coordinates='50,50,-50;150,50,-50;150,150,-50;50,150,-50;50,50,-30;150,50,-30;150,150,-30;50,150,-30',
        line_color=[0.7, 0.2, 0],
        is_bezier=False,
        is_bspline=False,
        is_3d=True
    )

def green_square():
    return create_new_object(
        name='VerdQuad',
        coordinates='600,100,-50;700,100,-40;700,200,-50;600,200,-40',
        line_color=[0.1, 0.8, 0],
        is_bezier=False,
        is_bspline=False
    )