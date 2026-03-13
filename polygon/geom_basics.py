"""
    Basic 2D geometry methods
"""
import math
import logging

def distance(p1,p2):
    delta_x = p1[0] - p2[0]
    delta_y=  p1[1] - p2[1]
    return math.sqrt((delta_x**2) + (delta_y**2))

def is_on_circle(center,radius,p,tolerance = 0.0001):
    dist = distance(center,p)
    return abs(dist - radius) < tolerance

def is_in_circle(center,radius,p):
    dist = distance(center,p)
    return dist <= radius

def circle_from_3_points(p1, p2, p3):
    """
    Returns: ((center_x, center_y), radius)
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    
    # Bereken het middelpunt met de formule voor de omgeschreven cirkel
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    
    if abs(d) < 1e-10:
        raise ValueError("Three points are on one line, no circle possible")
    
    ux = ((x1**2 + y1**2) * (y2 - y3) + 
          (x2**2 + y2**2) * (y3 - y1) + 
          (x3**2 + y3**2) * (y1 - y2)) / d
    
    uy = ((x1**2 + y1**2) * (x3 - x2) + 
          (x2**2 + y2**2) * (x1 - x3) + 
          (x3**2 + y3**2) * (x2 - x1)) / d
    
    center = (ux, uy)
    radius = math.sqrt((x1 - ux)**2 + (y1 - uy)**2)
    
    return center, radius

def bounding_box_from_center_radius(center, radius):
    center_x, center_y = center
    minx = center_x - radius
    miny = center_y - radius
    maxx = center_x + radius
    maxy = center_y + radius

    return (minx,miny), (maxx,maxy)

def calculate_endpoint(p1, angle_degrees, distance):
    """
    Calculate the endpoint p2 given a start point, angle, and distance.
    
    Args:
        p1: Tuple (x1, y1) representing the start point
        angle_degrees: Angle in degrees (0-180), measured from positive x-axis
        distance: Length of the line segment
    
    Returns:
        Tuple (x2, y2) representing the end point
    
    Note:
        -   0° points right (positive x direction)
        -  90° points up (positive y direction)
        - 180° points left (negative x direction)
    """
    x1, y1 = p1
    
    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)
    
    # Calculate the endpoint using trigonometry
    x2 = x1 + distance * math.cos(angle_radians)
    y2 = y1 + distance * math.sin(angle_radians)
    
    return (x2, y2)

def circle_intersections(c1, r1, c2, r2):
    """
    Calculate the intersection points of two circles.
    
    Args:
        c1: Tuple (x1, y1) - Center of circle 1
        r1: Radius of circle 1
        c2: Tuple (x2, y2) - Center of circle 2
        r2: Radius of circle 2
    
    Returns:
        A list of tuples containing intersection points.
        - Empty list [] if no intersection.
        - One tuple [(x, y)] if tangent.
        - Two tuples [(x, y), (x, y)] if they intersect at two points.
    """
    x1, y1 = c1
    x2, y2 = c2
    
    # Calculate distance between centers
    d = math.hypot(x2 - x1, y2 - y1)
    
    # Check for impossible cases
    # 1. Circles are too far apart
    if d > r1 + r2:
        return []
    # 2. One circle is completely inside the other
    if d < abs(r1 - r2):
        return []
    # 3. Concentric circles with different radii (d=0)
    if d == 0 and r1 != r2:
        return []
    # 4. Concentric circles with same radii (infinite intersections)
    if d == 0 and r1 == r2:
        raise ValueError("Circles are identical; infinite intersection points.")

    # Calculate the distance from c1 to the line connecting the intersection points
    # Using the Law of Cosines derivation
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    
    # Height from the line connecting centers to the intersection points
    h = math.sqrt(max(0, r1**2 - a**2)) # max(0, ...) handles floating point errors
    
    # Coordinates of the point P2 (the point on the line between centers closest to intersections)
    x2_temp = x1 + a * (x2 - x1) / d
    y2_temp = y1 + a * (y2 - y1) / d
    
    # Calculate the two intersection points
    x3_1 = x2_temp + h * (y2 - y1) / d
    y3_1 = y2_temp - h * (x2 - x1) / d
    
    x3_2 = x2_temp - h * (y2 - y1) / d
    y3_2 = y2_temp + h * (x2 - x1) / d
    
    return [(x3_1, y3_1), (x3_2, y3_2)]

def move(p,delta_matrix):
    new_x = p[0] + delta_matrix[0]
    new_y = p[1] + delta_matrix[1]
    return (new_x,new_y)

def rotate_point(p,angle):
    p_new = (
                (p[0]*math.cos(angle)) - (p[1] * math.sin(angle)),
                (p[0]*math.sin(angle)) + (p[1] * math.cos(angle))
            )
    return p_new

def get_angle_counter_clockwise(p):
        """
        (0,0) to (1,0)  =>   0 degrees
        (0,0) to (0,1)  =>  90 degrees
        (0,0) to (-1,0) => 180 degrees
        (0,0) to (0,-1) => 270 degrees
        """
        x,y = p
        base_angle = 0
        if x == 0 and y > 0:
            return 90
        elif x == 0 and y < 0:
            return 270
        elif x >= 0 and y == 0:
            return 0
        elif x < 0 and y == 0:
            return 180
        else:
            base_angle = math.degrees(math.atan(y/x))
            logging.debug(f'base_angle = {base_angle}')

        if x > 0 and y > 0:
            return base_angle
        elif x > 0 and y < 0:
            return base_angle + 360
        elif x  < 0 and y > 0:
            return base_angle + 180
        elif x < 0 and y < 0:
            return base_angle + 180
        
def caculate_angle_counter_clockwise(p1,p2,p3):
    """
    get the angle from the line p2-p3 to the line p2 - p1 in the counter clockwise direction
                  p3
          angle  /
                /
    p1--------p2
    """

    # move to new coordinate system with p2 at 0,0
    delta=(-p2[0],-p2[1])
    p1_a = move(p1,delta)
    p3_a = move(p3,delta)

    logging.debug(f"p1= {p1} , p2 = {p2} , p3={p3}")
    logging.debug(f"p1_a= {p1_a} , p3_a={p3_a}")
    
    angle_1 = get_angle_counter_clockwise(p1_a)
    angle_2 = get_angle_counter_clockwise(p3_a)

    logging.debug(f"angle_1= {angle_1} , angle_2 = {angle_2}")
    diff_angle = angle_2 - angle_1
    if diff_angle < 0:
        return diff_angle + 360
    else:
        return diff_angle

