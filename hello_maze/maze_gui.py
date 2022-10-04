from maze import *
import PySimpleGUIQt as sg
import logging

class MazeConfiguration:

    def __init__(self):
        self.default_game_size = Size(4,4)

class MazeController:

    def __init__(self):
        self.show_short_path = False
        
        self.square_width = 4
        self.wall_width = 4
        self.maze_img = None

        self.nr_of_cols:int = 4
        self.nr_of_rows:int = 4
        self.generate_new()
    
    def reset_game(self):
        self.game = MazeGame(self.maze_gen.maze,square_width=self.square_width,wall_width=self.wall_width)

        self.short_path_renderer = ImageGameGridRender(self.game.game_grid)
        blank_map:dict(str,tuple[int,int,int]) = dict()
        blank_map[Material.FLOOR_MARKED.value] = Color.WHITE.value
        self.blank_renderer = ImageGameGridRender(self.game.game_grid,material_map=blank_map)
        self._set_renderer()
        self.render()

    def generate_new(self):
        self.maze_gen =  MazeGenerator(Size(self.nr_of_cols,self.nr_of_rows))
        self.reset_game()

    def _set_renderer(self):
        self.renderer = self.blank_renderer
        if self.show_short_path:
            self.renderer = self.short_path_renderer 

    def render(self):
        self.renderer.render()
        self.maze_img = self.renderer.output

    def set_show_short_path(self,value:bool):
        if self.show_short_path != value:
            self.show_short_path = value
            self._set_renderer()
            self.render()

    # just for testing
    def add_particle(self):
        for col in range(0,self.game.game_grid.size.nr_of_cols):
            content = self.game.game_grid.get_location((col,0))
            if not content.solid and content.guest == None:
                content.guest = Particle()
                break
        self.render()


class MazeDialog:

    def __init__(self,config:MazeConfiguration):
        self.config = config
        self.controller = MazeController()
        self.maze_display_img  = None
        self.maze_max_width = 600
        self.maze_img_dim = (self.maze_max_width,400)
        self.right_width = 200
        left_frame = [
            [sg.Image(filename='', key='_IMAGE_',size=self.maze_img_dim)]
        ]
        right_frame = [ 
          #  [   sg.Text("Name:"),
          #      sg.Input(key='__NAME__',size=(self.right_width - 35,sg.DEFAULT_ELEMENT_SIZE[1]))
          #  ],
            [   sg.Text('Debug logging'),
                sg.Radio('On', 1,enable_events=True,key='__LOG_ON__'),
                sg.Radio('Off', 1, default=True,key='__LOG_OFF__')
            ],
            [   sg.Text('Show shortest path'),
                sg.Radio('On', 1,enable_events=True,key='__SHORT_ON__'),
                sg.Radio('Off', 1, default=True,key='__SHORT_OFF__')
            ],
            
            [sg.Text('Nr of columns',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Slider(range=(1,50),key='__NR_OF_COLS__',default_value=self.controller.nr_of_cols,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Text('Nr of rows')],
            [sg.Slider(range=(1,40),key='__NR_OF_ROWS__',default_value=self.controller.nr_of_rows,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],

            [sg.Text('Square width',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Slider(range=(1,20),key='__SQUARE_WIDTH__',default_value=self.controller.square_width,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Text('Wall width')],
            [sg.Slider(range=(1,20),key='__WALL_WIDTH__',default_value=self.controller.wall_width,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Add particle',key='__ADD_PARTICLE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Reset maze',key='__RESET_MAZE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Generate new',key='__GENERATE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Quit',key='__QUIT__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))]
        ]
        layout = [  
            [sg.Frame("", left_frame),sg.Frame("", right_frame)]
        ]
        self.window = sg.Window('Maze simulator', layout)

    def update_current_images(self):
        if not self.controller.maze_img is None:
            self.maze_display_img= cv2.resize(self.controller.maze_img, self.maze_img_dim, interpolation = cv2.INTER_AREA)

    def update_dialog(self):
        #self.controller.render()
        self.update_current_images()
        if not self.maze_display_img is None:
            imgbytes=cv2.imencode('.png', self.maze_display_img)[1].tobytes()
            self.window.FindElement('_IMAGE_').Update(data=imgbytes)

    def run(self):
        while True:
            event, values = self.window.Read(timeout=20, timeout_key='timeout')
            if event is None or event == '__QUIT__':
                break
            if event == '__ADD_PARTICLE__':
                logging.debug("Add particle")
                self.controller.add_particle()
            if event == '__RESET_MAZE__':
                logging.debug("Resetting maze")
                self.controller.reset_game()
                logging.debug("Reset maze ready")
            if event == '__GENERATE__':
                logging.debug("Generate button pressed")
                self.controller.generate_new()
            if event == '__SHORT_ON__':
                self.controller.set_show_short_path(values['__SHORT_ON__'])
            if event == '__LOG_ON__':
                debug = values['__LOG_ON__']
                if debug:
                    logging.basicConfig(level=logging.DEBUG,force=True)
                else:
                    logging.basicConfig(level=logging.ERROR,force=True)

            self.update_nr_of_cols(values['__NR_OF_COLS__'])
            self.update_nr_of_rows(values['__NR_OF_ROWS__'])
            self.update_square_width(values['__SQUARE_WIDTH__'])
            self.update_wall_width(values['__WALL_WIDTH__'])

            self.update_dialog()
        self.window.close()

    def update_nr_of_cols(self,value:int):
        self.controller.nr_of_cols = value

    def update_nr_of_rows(self,value:int):
        self.controller.nr_of_rows = value

    def update_square_width(self,value:int):
        self.controller.square_width = value

    def update_wall_width(self,value:int):
        self.controller.wall_width = value

def main():
    conf = MazeConfiguration()
    dialog = MazeDialog(conf)
    dialog.run()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    main()