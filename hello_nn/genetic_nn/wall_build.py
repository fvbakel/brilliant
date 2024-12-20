from random import randrange,choice

from typing import Callable

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

def generate_wall_positions(wall_mode: str, size: Size):

    wall_functions: dict[str, Callable[[Size]]] = {
        WallMode.TWO.value: two_walls,
        WallMode.SMALL.value: small_walls,
        WallMode.DIAG.value: diag_walls,
        WallMode.ARROW.value: arrow_walls,
        WallMode.BUCKET.value: bucket_walls,
        WallMode.BUCKET_HOLE.value: lambda s: bucket_hole_walls(s, 1)
    }

    if wall_mode == WallMode.RANDOM.value:
        random_mode = choice([mode.value for mode in WallMode if mode != WallMode.RANDOM])
        return generate_wall_positions(random_mode, size)

    if wall_mode in wall_functions:
        return wall_functions[wall_mode](size), wall_mode
    else:
        raise ValueError(f'Unexpected wall mode {wall_mode}. Please use one of {list(wall_functions.keys())}')

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