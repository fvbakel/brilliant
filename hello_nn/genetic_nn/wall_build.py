from random import randrange

from basegrid import (
    Size,Position, ExtendedEnum
)

class WallMode(ExtendedEnum):
    TWO         = 'two'
    SMALL       = 'small'
    DIAG        = 'diag'
    ARROW       = 'arrow'
    BUCKET      = 'bucket'
    BUCKET_HOLE = 'bucket_hole'
    RANDOM      = 'random'

def generate_wall_positions(wall_mode:str, size: Size):
    if wall_mode == WallMode.TWO.value:
        return two_walls(size)
    elif wall_mode == WallMode.SMALL.value:
        return small_walls(size)
    elif wall_mode == WallMode.DIAG.value:
        return diag_walls(size) 
    elif wall_mode == WallMode.ARROW.value:
        return arrow_walls(size) 
    elif wall_mode == WallMode.BUCKET.value:
        return bucket_walls(size) 
    elif wall_mode == WallMode.BUCKET_HOLE.value:
        return bucket_hole_walls(size,1) 
    elif wall_mode == WallMode.RANDOM.value:
        modes = WallMode.list()
        index = randrange(0,len(modes) -1)
        return generate_wall_positions(modes[index],size) 
    else:
        raise ValueError(f'Unexpected wall mode {wall_mode} please use one of {WallMode.list()}')

"""
    wall_edge_free   1/10
    wall_size        3/10
    hole_size        2/10
    wall_size        3/10
    wall_edge_free   1/10
    ---------------------
    Total            10/10
"""
def two_walls(size:Size):
    wall_positions:set[Position] = set()

    wall_col            = round(size.nr_of_cols * 0.2) + 1

    wall_size           = (size.nr_of_rows // 10) * 3
    wall_edge_free      = (size.nr_of_rows // 10)
    hole_size           = size.nr_of_rows // 5

    wall_row_start      = wall_edge_free
    wall_row_hole_start = wall_row_start + wall_size
    wall_row_hole_end   = wall_row_hole_start + hole_size

    wall_positions = wall_positions.union(vertical_wall(wall_col, wall_row_start,wall_size))
    wall_positions = wall_positions.union(vertical_wall(wall_col, wall_row_hole_end,wall_size))

    return wall_positions

def small_walls(size:Size):
    wall_positions:set[Position] = set()

    wall_size           = (size.nr_of_rows // 16)
    nr_of_walls         = 25
    for i in range(0,nr_of_walls):
        col       = randrange(0,size.nr_of_cols)
        start_row = randrange(0,size.nr_of_rows - wall_size)
        wall_positions = wall_positions.union(vertical_wall(col, start_row,wall_size))

    return wall_positions



def diag_walls(size:Size):
    wall_positions:set[Position] = set()

    wall_size           = (size.nr_of_rows // 16)
    nr_of_walls         = 25
    for i in range(0,nr_of_walls):
        col_start   = randrange(0,size.nr_of_cols - wall_size)
        start_row   = randrange(0,size.nr_of_rows - wall_size)
        wall_positions = wall_positions.union(diag_wall_right_down(col_start,start_row,wall_size))

    return wall_positions

def arrow_walls(size:Size):
    wall_positions:set[Position] = set()

    wall_size           = (size.nr_of_rows // 20)
    nr_of_walls         = 25
    for i in range(0,nr_of_walls):
        col_start   = randrange(0,size.nr_of_cols - (wall_size * 2))
        start_row   = randrange(0,size.nr_of_rows - (wall_size * 2))

        wall_positions = wall_positions.union(arrow_wall(col_start,start_row,wall_size))
                    
    return wall_positions

def bucket_walls(size:Size):
    return bucket_hole_walls(size,0)

def bucket_hole_walls(size:Size,hole_size:int):
    wall_positions:set[Position] = set()

    wall_size           = (size.nr_of_rows // 20)
    nr_of_walls         = 25
    for i in range(0,nr_of_walls):
        col_start   = randrange(wall_size,size.nr_of_cols - (wall_size * 2))
        start_row   = randrange(0,size.nr_of_rows - (wall_size * 2) - hole_size)
        wall_positions = wall_positions.union(bucket_hole_wall(col_start,start_row,wall_size,hole_size))
    return wall_positions

def arrow_wall(col_start:int,start_row:int,wall_size:int):
    wall_positions:set[Position] = set()
    wall_positions = wall_positions.union(diag_wall_right_down(col_start,start_row,wall_size))
    start_row = start_row + wall_size
    wall_positions = wall_positions.union(diag_wall_left_down((col_start + wall_size - 1) ,start_row,wall_size))

    return wall_positions

def bucket_hole_wall(col_start:int,start_row:int,wall_size:int,hole_size:int):
    wall_positions:set[Position] = set()
    wall_positions = wall_positions.union(diag_wall_left_down(col_start,start_row,wall_size))
    start_row = start_row + wall_size + hole_size
    wall_positions = wall_positions.union(diag_wall_right_down((col_start - wall_size + 1) ,start_row,wall_size))

    return wall_positions

def vertical_wall(col:int, start_row:int, wall_size:int):
    wall_positions:set[Position] = set()
    for row in range(start_row,start_row + wall_size):
        pos = Position(col=col,row=row)
        wall_positions.add(pos)
    return wall_positions

def diag_wall_right_down(col_start:int,start_row:int,wall_size:int):
    wall_positions:set[Position] = set()
    col = col_start
    for row in range(start_row,start_row + wall_size):
        pos = Position(col=col,row=row)
        wall_positions.add(pos)
        col = col + 1
    return wall_positions

def diag_wall_left_down(col_start:int,start_row:int,wall_size:int):
    wall_positions:set[Position] = set()
    col = col_start
    for row in range(start_row,start_row + wall_size):
        pos = Position(col=col,row=row)
        wall_positions.add(pos)
        col = col - 1
    return wall_positions