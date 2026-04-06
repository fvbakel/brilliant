import cadquery as cq
from cadquery.func import *

e = segment((0,0), (0,1))

c = circle(1)


result = compound(e, c)


if __name__ == "__main__":
    from cadquery.vis import show

    options = opt={
            "width": 300,
            "height": 300,
            "marginLeft": 10,
            "marginTop": 10,
            "showAxes": False,
            "projectionDir": (0, 0, 1),
            "strokeWidth": 0.05,
            "strokeColor": (255, 0, 0),
            "hiddenColor": (0, 0, 255),
            "showHidden": False,
        }

    result.export(
        "./tmp/2d-drawing.svg",
        opt={
            "width": 300,
            "height": 300,
            "marginLeft": 0,
            "showAxes": True,
            "projectionDir": (0, 0, -1),
            "strokeWidth": 0.01,
            "strokeColor": (255, 0, 0),
            "hiddenColor": (0, 0, 255),
            "showHidden": False,
        },
    )
else:
    show_object(result)