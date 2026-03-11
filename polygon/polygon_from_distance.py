import geom_basics as gb
import matplotlib.pyplot as plt
    
def normalize_angle(angle):
    if angle <= 0:
        angle = angle + 360
    return angle

def get_next_point(center,radius,start_angle,p2,d):
    intersection = gb.circle_intersections(center,radius,p2,d)

    previous_angle = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,p2)
    angle_abs_1 = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,intersection[0])
    angle_abs_2 = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,intersection[1])

    

    previous_rel_angle = normalize_angle(previous_angle - start_angle)
    angle_rel_1 = normalize_angle(angle_abs_1 - start_angle)
    angle_rel_2 = normalize_angle(angle_abs_2 - start_angle)

    print(f"print: start_angle=        {start_angle}")
    print(f"print: previous_abs_angle= {previous_angle}")
    print(f"print: angle_abs_1 =       {angle_abs_1}")
    print(f"print: angle_abs_2 =       {angle_abs_2}")

    print(f"print: previous_rel_angle= {previous_rel_angle}")
    print(f"print: angle_rel_1 =       {angle_rel_1}")
    print(f"print: angle_rel_2 =       {angle_rel_2}")

    if angle_rel_1 > previous_rel_angle and angle_rel_1 < 360:
        print("Choose 1")
        return intersection[0]
    elif angle_rel_2 > previous_rel_angle and angle_rel_2 < 360:
        print("Choose 2")
        return intersection[1]
    else:
        print("Choose none")
        return None

def calculate_polygon(distances,max_loop=100,tolerance = 0.001):
    """
    Given the lenght of the edges of a polygon,
    reconstruct the maximum polygon.
    given is that all points are on the same circle
    """
    d_1 = distances[0]
    d_2 = distances[1]
    p1 = (0,0)
    p2 = (d_1,0)

    nr_of_points = len(distances)

    min_angle = 0
    max_angle = 180
    angle = min_angle + (max_angle - min_angle) / 2
    loop = 0
    center = []
    radius = 0
    points = []
    while loop < max_loop:
        loop += 1
        cur_index = 2
        angle = min_angle + (max_angle - min_angle) / 2
        p3 = gb.calculate_endpoint(p2,angle,d_2)
        center, radius = gb.circle_from_3_points(p1,p2,p3)
        start_angle = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,p1)
        points = []
        points.append(p1)
        points.append(p2)
        points.append(p3)
        p_next = None
        while cur_index < nr_of_points:
            p_next = get_next_point(center,radius,start_angle,points[cur_index],distances[cur_index])
            if p_next is None:
                break
            points.append(p_next)
            cur_index += 1

        if p_next is None:
            max_angle = angle
        else:
            dist = gb.distance(p1,points[-1])
            print(dist)
            if dist < tolerance:
                print("Found solution")
                break
            else:
                min_angle = angle

        #make_picture(center, radius, points[:-1],id=f"_{loop}_{angle}")
    
    return center, radius, points[:-1]
    
        
def make_picture(center,radius,points,id=""):
    fig, ax = plt.subplots() 
    ax.set_aspect('equal') 

    # Set appropriate axis limits
    bb1,bb2 = gb.bounding_box_from_center_radius(center,radius)
    ax.set_xlim(bb1[0], bb2[0])
    ax.set_ylim(bb1[1], bb2[1])

    circle = plt.Circle(center, radius, color='purple',fill=False)
    ax.add_patch(circle)

    # lines and points
    for index,point in enumerate(points):
        if index == len(points) - 1:
            next_point = points[0]
        else:
            next_point = points[index +1]
        line = plt.Line2D((point[0],next_point[0]),(point[1],next_point[1]))
        ax.add_line(line)
        ax.annotate(f'p {index+1}', xy = point, xytext = point)

    fig.savefig(f"./tmp/test{id}.png")


if __name__ == "__main__":
    center, radius, points = calculate_polygon([2,4,1,3,2])
    make_picture(center, radius, points)