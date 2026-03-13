import geom_basics as gb
import matplotlib.pyplot as plt
import pandas as pd
import logging
from shapely.geometry import Polygon
from pathlib import Path


def normalize_angle(angle):
    if angle <= 0:
        angle = angle + 360
    return angle

def get_next_point(center,radius,start_angle,p2,d):
    intersection = gb.circle_intersections(center,radius,p2,d)

    if len(intersection) == 0:
        logging.error("New circle does not intersect")
        # TODO raise error instead
        return None

    previous_angle = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,p2)
    angle_abs_1 = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,intersection[0])
    angle_abs_2 = gb.caculate_angle_counter_clockwise((center[0]+1,center[1]),center,intersection[1])

    

    previous_rel_angle = normalize_angle(previous_angle - start_angle)
    angle_rel_1 = normalize_angle(angle_abs_1 - start_angle)
    angle_rel_2 = normalize_angle(angle_abs_2 - start_angle)

    logging.debug(f"start_angle=        {start_angle}")
    logging.debug(f"previous_abs_angle= {previous_angle}")
    logging.debug(f"angle_abs_1 =       {angle_abs_1}")
    logging.debug(f"angle_abs_2 =       {angle_abs_2}")

    logging.debug(f"previous_rel_angle= {previous_rel_angle}")
    logging.debug(f"angle_rel_1 =       {angle_rel_1}")
    logging.debug(f"angle_rel_2 =       {angle_rel_2}")

    if angle_rel_1 > previous_rel_angle and angle_rel_1 < 360:
        logging.debug("Choose 1")
        return intersection[0]
    elif angle_rel_2 > previous_rel_angle and angle_rel_2 < 360:
        logging.debug("Choose 2")
        return intersection[1]
    else:
        logging.debug("Choose none")
        return None

def rotate_distances(distances):
    max_index = distances.index(max(distances))
    return distances[max_index:] + distances[:max_index]


def calculate_polygon(distances_input,max_loop=100,tolerance = 0.000001):
    """
    Given the lenght of the edges of a polygon,
    reconstruct the maximum polygon.
    given is that all points are on the same circle
    """
    distances=rotate_distances(distances_input)
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
    solution_found = False
    while loop < max_loop:
        loop += 1
        cur_index = 2
        angle = min_angle + (max_angle - min_angle) / 2
        p3 = gb.calculate_endpoint(p2,angle,d_2)
        try:
            center, radius = gb.circle_from_3_points(p1,p2,p3)
        except ValueError as e:
            logging.error(e)
            #todo check what to do in this case, because should not happen
            break

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
            logging.debug(f'found distance of last endpoint to startpoint: {dist}')
            if dist < tolerance:
                logging.debug("Found solution")
                solution_found = True
                break
            else:
                min_angle = angle

        #make_picture(center, radius, points[:-1],id=f"_{loop}_{angle}")
    
    return solution_found, center, radius, points[:-1]
    
        
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
    plt.close()

def get_area(points):
    return Polygon(points).area

def polygon_for_file(filename,stop_at=None):
    df = pd.read_csv(filename)

    output_file = f"{TEST_TMP_DIR}/{Path(filename).stem}_output.csv" 
    with open(output_file, "w", encoding="utf-8") as f:
        df = df.astype({"id": int, "CE":bool})
        nr_found = 0
        for index, row in df.iterrows():
            distances = row.values.flatten().tolist()[1:-2]
            #                                                                                      .8801807054043796
            found, center, radius, points = calculate_polygon(distances,max_loop=1000,tolerance = 0.000000001 )
            area = None
            if found:
                nr_found +=1
                area = get_area(points)
            row_str = ",".join(str(val) for val in row.values.flatten().tolist())
            f.write(f'{row_str}, {found},{center[0]},{center[1]},{radius},{area}\n')

            if ((index+1) % 50) == 0:
                print(f'lines processed: {index +1}, nr_found: {nr_found}, success rate: {((index+1) / nr_found) * 100:.2f} %')
                make_picture(center,radius,points,id=f'_{index}')
            if stop_at is not None and index +1 == stop_at:
                print(f'Stopping at {index}')
                break
        print(f'nr_found = {nr_found}')        

TEST_TMP_DIR = "./tmp"
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,filename=f"{TEST_TMP_DIR}/test_debug.log",filemode='w')
    #found, center, radius, points = calculate_polygon([2,4,1,3,2])
    #make_picture(center, radius, points)

    polygon_for_file('data/kaggle_train_5_fences.csv',stop_at=None)