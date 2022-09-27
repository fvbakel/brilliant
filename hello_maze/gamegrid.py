
from basegrid import *

class Material(Enum):
    NONE                  = '_'
    FLOOR                 = 'F'
    FLOOR_MARKED          = 'f'
    FLOOR_HIGHLIGHTED     = 'H'
    STONE                 = 'S'
    PLASTIC               = 'P'
    PLASTIC_MARKED        = 'p'
    PLASTIC_HIGHLIGHTED   = '0'

class GameContent:
    def __init__(self):
        self.solid:bool         = False
        self.mobile:bool        = False
        self.guest:GameContent  = None
        self.material           = Material.FLOOR


class Floor(GameContent):
    def __init__(self):
        super().__init__()
        self.solid:bool         = False
        self.mobile:bool        = False
        self.material           = Material.FLOOR

class Wall(GameContent):
    def __init__(self):
        super().__init__()
        self.solid:bool     = True
        self.mobile:bool    = False
        self.material       = Material.STONE

class Particle(GameContent):
    def __init__(self):
        super().__init__()
        self.solid:bool     = True
        self.mobile:bool    = True
        self.material       = Material.PLASTIC
   

class GameGrid(Grid):
    
    def __init__(self,grid_size:Size):
        super().__init__(grid_size)

class GameGridRender:

    def __init__(self,maze_grid:GameGrid):
        self.maze_grid = maze_grid
        self.output=None

    def _pre_render(self):
        self.output=None
    
    def _post_render(self):
        pass

    def render(self):
        self._pre_render()
        for row in range(0,self.maze_grid.size.nr_of_rows):
            self._render_row(row)
        self._post_render()

    def _render_row(self,row:int):
        for col in range(0,self.maze_grid.size.nr_of_cols):
            self._render_location(self.maze_grid.get_location((col,row)))
    
    def _render_location(self,location:Location):
        material = self._get_material(location.content)
        self._render_material(location.position,material)
        
    def _get_material(self,content:GameContent) -> Material:
        if content == None:
            return Material.NONE

        if content.guest != None:
            return self._get_material(content.guest)

        return content.material

    def _render_material(self,position:(Position | tuple[int,int]),material:Material):
        pass

class TextMazeGridRender(GameGridRender):

    def __init__(self,maze_grid:GameGrid):
        super().__init__(maze_grid)
        self.output = ""

    def _pre_render(self):
        self.output = ""

    def _render_row(self,row:int):
        self.output += "\n"
        super()._render_row(row)

    def _render_material(self,position:(Position | tuple[int,int]),material:Material):
        self.output += str(material.value)

