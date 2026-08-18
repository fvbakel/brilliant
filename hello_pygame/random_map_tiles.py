import pygame
import random

class TileDefinition:

    def __init__(self,name:str,location:tuple[int,int],
                 has_north:bool,
                 has_east:bool,
                 has_south:bool,
                 has_west:bool
                 ):
        self.name:str = name
        self.location = location
        self.tile_size      = 32
        self.tile_spacing   = 1

        self.has_north:bool = has_north
        self.has_east: bool = has_east
        self.has_south:bool = has_south
        self.has_west: bool = has_west

    def get_rect(self):
        tx, ty = self.location

        # Account for the 1-pixel spacing between tiles
        source_x = tx * (self.tile_size + self.tile_spacing) + self.tile_spacing
        source_y = ty * (self.tile_size + self.tile_spacing) + self.tile_spacing

        return pygame.Rect(
            source_x,
            source_y,
            self.tile_size,
            self.tile_size,
        )

class TileSet:
    def __init__(self):
        self.file = 'simple_spacing_4_rows.png'
        self.image:pygame.Surface
        self.tile_defs:dict[str,TileDefinition] = dict()
        self.tile_size      = 32
        self.tile_spacing   = 1
        self._make_defs()

    def _make_defs(self):
        self._add_tile_def('cross',(0, 0),True,True,True,True)
        self._add_tile_def('c-nw', (1, 0),True,False,False,True)
        self._add_tile_def('c-ne', (2, 0),True,True,False,False)
        self._add_tile_def('horz', (3, 0),False,True,False,True)
        self._add_tile_def('T-n',  (0, 1),True,True,False,True)
        self._add_tile_def('c-se', (1, 1),False,True,True,False)
        self._add_tile_def('c-sw', (2, 1),False,False,True,True)
        self._add_tile_def('vert', (3, 1),True,False,True,False)
        self._add_tile_def('T-e',  (0, 2),True,True,True,False)
        self._add_tile_def('T-s',  (1, 2),False,True,True,True)
        self._add_tile_def('T-w',  (2, 2),True,False,True,True)
        self._add_tile_def('none', (3, 2),False,False,False,False)

    def _add_tile_def(self,name:str,location:tuple[int,int],
                      has_north:bool,
                      has_east:bool,
                      has_south:bool,
                      has_west:bool
                      ):
        tile_def = TileDefinition(name,location,has_north,has_east,has_south,has_west)
        self.tile_defs[name] = tile_def

    def load_image(self):
        self.image = pygame.image.load(self.file).convert_alpha()


class TileMap:

    def __init__(self,tile_set:TileSet):
        self.tile_width  = 20
        self.tile_height = 10
        self.tile_set = tile_set
        none_tile = self.tile_set.tile_defs['none']

        self.tiles:list[list[TileDefinition]] = []
        for row in range(self.tile_height):
            self.tiles.append([none_tile] * self.tile_width)



    def make_random(self):
        for row in range(self.tile_height):
            for col in range(self.tile_width):
                to_choose_from:list[TileDefinition] = list()

                if row == 0 and col == 0:
                    to_choose_from = list(self.tile_set.tile_defs.values())
                if row != 0 and col == 0:
                    north_tile = self.tiles[row-1][col]
                    to_choose_from = [tile_def for tile_def 
                                      in self.tile_set.tile_defs.values() 
                                      if tile_def.has_north == north_tile.has_south
                                     ]
                if row == 0 and col != 0:
                    west_tile = self.tiles[row][col-1]
                    to_choose_from = [tile_def for tile_def 
                                        in self.tile_set.tile_defs.values() 
                                        if tile_def.has_west == west_tile.has_east
                                    ]
                if row != 0 and col != 0:
                    north_tile = self.tiles[row-1][col]
                    west_tile = self.tiles[row][col-1]
                    to_choose_from = [tile_def for tile_def 
                                        in self.tile_set.tile_defs.values() 
                                        if  tile_def.has_west  == west_tile.has_east   and
                                            tile_def.has_north == north_tile.has_south
                                    ]
                 
                selected = random.choice(to_choose_from)
                self.tiles[row][col] = selected

class UserInterface():

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Random map generator")
        self.rendered:bool = False

        self.tile_set = TileSet()
        self.tile_map = TileMap(self.tile_set)
        
        self.clock = pygame.time.Clock()

        self.width  = self.tile_map.tile_width  * self.tile_set.tile_size
        self.height = self.tile_map.tile_height * self.tile_set.tile_size

        self.window = pygame.display.set_mode((self.width,self.height))
        self.tile_set.load_image()
        self.running = True

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_r:
                    self.tile_map.make_random()
                    self.rendered = False
                    break

    def render(self):

        if not self.rendered:
            self.window.fill("white")
            
            for row in range(self.tile_map.tile_height):
                for col in range(self.tile_map.tile_width):
                    tile_def = self.tile_map.tiles[row][col]
                    source_rect = tile_def.get_re
            
                    # Position on the map
                    destination = (
                        col * self.tile_set.tile_size,
                        row * self.tile_set.tile_size,
                    )
            
                    self.window.blit(self.tile_set.image, destination, source_rect)
            
            pygame.display.flip()
            self.rendered = True

    def run(self):
        while self.running:
            self.process_input()
            self.render()
            self.clock.tick(60)


userInterface = UserInterface()
userInterface.run()

pygame.quit()