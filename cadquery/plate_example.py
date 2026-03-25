import cadquery as cq
from cadquery.vis import show_object,show
result = ( 
    cq.Workplane("XY" )
    .box(3, 3, 0.5)
    .edges("|Z")
    .fillet(0.125)
)


inGui = False
if inGui:
    show_object(result)
else:
    show(result)
