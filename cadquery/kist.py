import cadquery as cq

plank_breedte = 100
plank_dikte   = 15

kist_lengte  = 1000
kist_breedte = 6 * plank_breedte
kist_hoogte  = 5 * plank_breedte


def make_lengte_plank():
    plank = (
        cq.Workplane("XY" )
        .box(plank_breedte, kist_lengte, plank_dikte)
    )
    return plank

def make_breedte_plank():
    plank = (
        cq.Workplane("XY" )
        .box(plank_breedte, kist_breedte-(plank_dikte*2), plank_dikte)
    )
    return plank

def make_hoogte_plank():
    plank = (
        cq.Workplane("XY" )
        .box(plank_breedte, kist_hoogte, plank_dikte)
    )
    return plank

def make_handvat():
    plank = (
        cq.Workplane("XY" )
        .box((plank_breedte/2), kist_breedte, plank_dikte)
    )
    return plank

def make_kopkant():
    local_color = cq.Color("green")
    kopkant = cq.Assembly()
    nr_of_plank = kist_hoogte // plank_breedte
    for i in range(0,nr_of_plank):
        kopkant.add(make_breedte_plank(),name=f"kopkant_{i}", loc=cq.Location(plank_breedte*i,0,0,0,0,0),color=local_color)
    kopkant.add(make_hoogte_plank(),
                name=f"kopkant_hoogte_links", 
                loc=cq.Location(
                    (kist_hoogte/2) - (plank_breedte/2),
                    ((kist_breedte-(2*plank_dikte))/2)-(plank_breedte/2),
                    plank_dikte,0,180,90
                ), 
                color=local_color
                )
    kopkant.add(make_hoogte_plank(),
                name=f"kopkant_hoogte_rechts", 
                loc=cq.Location(
                    (kist_hoogte/2) - (plank_breedte/2),
                    -((kist_breedte-(2*plank_dikte))/2)+(plank_breedte/2),
                    plank_dikte,0,180,90
                ), 
                color=local_color
                )
    kopkant.add(make_handvat(),
                name=f"kopkant_handvat", 
                loc=cq.Location(
                    kist_hoogte - 1.5*plank_breedte,
                    0,
                    plank_dikte*2,0,0,0
                ), 
                color=local_color
                )
    
    return kopkant

def make_zijkant():
    zijkant_color = cq.Color("blue")
    zijkant = cq.Assembly()
    nr_of_plank = kist_hoogte // plank_breedte
    for i in range(0,nr_of_plank):
        zijkant.add(make_lengte_plank(), name=f"zijkant{i}", loc=cq.Location(plank_breedte*i,0,0,0,0,0),color=zijkant_color)
                  
    return zijkant

def make_bodem():
    bodem = cq.Assembly()
    nr_of_plank = kist_breedte // plank_breedte
    for i in range(0,nr_of_plank):
        bodem.add(make_lengte_plank(), name=f"bodem_{i}", loc=cq.Location(plank_breedte*i,0,0,0,0,0),color=cq.Color("yellow"))
                  
    return bodem

kist = (
    cq.Assembly()
    .add(make_bodem(), name="bodem")
    .add(make_kopkant(), name="kopkant_voor",loc=cq.Location(
        (kist_breedte/2)-((plank_breedte/2)),
        -(kist_lengte/2) + plank_dikte + (plank_dikte/2),
        (plank_breedte/2)+(plank_dikte/2)
        ,0,270,90)
        )
    .add(make_kopkant(), name="kopkant_achter",loc=cq.Location(
        (kist_breedte/2)-((plank_breedte/2)),
        (kist_lengte/2) - plank_dikte - (plank_dikte/2),
        ((plank_breedte/2) +(plank_dikte/2)) 
        ,0,270,270)
        )
    .add(make_zijkant(), name="zijkant_links",loc=cq.Location(
        -((plank_breedte/2)-plank_dikte/2),
        0,
        kist_hoogte - ((plank_breedte/2)-(plank_dikte/2)) 
        ,0,90,0)
        )
    .add(make_zijkant(), name="zijkant_rechts",loc=cq.Location(
        -((plank_breedte/2)-plank_dikte/2)+kist_breedte-plank_dikte,
        0,
        kist_hoogte - ((plank_breedte/2)-(plank_dikte/2)) 
        ,0,90,0)
        )

)


inGui = True
if inGui:
    show_object(kist)
else:
    from cadquery.vis import show
    show(kist)