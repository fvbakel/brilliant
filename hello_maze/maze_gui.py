from maze import *
import PySimpleGUIQt as sg
import logging

class MazeConfiguration:

    def __init__(self):
        self.default_game_size = Size(4,4)

class MazeController:

    def __init__(self):
        self.show_short_path = False
        self.maze_size = Size(4,4)
        self.square_width = 4
        self.wall_width = 4
        self.maze_img = None
        self.generate_new()

    def generate_new(self):
        maze_gen =  MazeGenerator(self.maze_size)
        self.game = MazeGame(maze_gen.maze,square_width=self.square_width,wall_width=self.wall_width)

        self.short_path_renderer = ImageGameGridRender(self.game.game_grid)
        blank_map:dict(str,tuple[int,int,int]) = dict()
        blank_map[Material.FLOOR_MARKED.value] = Color.WHITE.value
        self.blank_renderer = ImageGameGridRender(self.game.game_grid,material_map=blank_map)
        self.renderer = self.blank_renderer
        self.render()

    
    def render(self):
        self.renderer.render()
        self.maze_img = self.renderer.output




class MazeDialog:

    def __init__(self,config:MazeConfiguration):
        self.config = config
        self.controller = MazeController()
        self.maze_display_img  = None
        self.maze_max_width = 600
        self.maze_img_dim = (self.maze_max_width,200)
        self.right_width = 200
        left_frame = [
            [sg.Image(filename='', key='_IMAGE_',size=self.maze_img_dim)]
        ]
        right_frame = [ 
            [   sg.Text("Name:"),
                sg.Input(key='__NAME__',size=(self.right_width - 35,sg.DEFAULT_ELEMENT_SIZE[1]))
            ],
            [   sg.Text('Show shortest path'),
                sg.Radio('On', 1,enable_events=True,key='__SHORT_ON__'),
                sg.Radio('Off', 1, default=True,key='__SHORT_OFF__')
            ],
            
            [sg.Text('Nr of columns',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Slider(range=(4,50),key='__NR_OF_COLS__',default_value=10,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Text('Nr of rows')],
            [sg.Slider(range=(4,40),key='__NR_OF_ROWS__',default_value=5,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],

            [sg.Text('Square width',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Slider(range=(4,10),key='__SQUARE_WIDTH__',default_value=4,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Text('Wall width')],
            [sg.Slider(range=(1,5),key='__WALL_WIDTH__',default_value=2,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],

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
        self.update_current_images()
        if not self.maze_display_img is None:
            imgbytes=cv2.imencode('.png', self.maze_display_img)[1].tobytes()
            self.window.FindElement('_IMAGE_').Update(data=imgbytes)

    def run(self):
        while True:
            event, values = self.window.Read(timeout=20, timeout_key='timeout')
            if event is None or event == '__QUIT__':
                break
            if event == '__GENERATE__':
                logging.debug("Generate button pressed")
                self.controller.generate_new()
            self.update_dialog()
        self.window.close()

def main():
    conf = MazeConfiguration()
    dialog = MazeDialog(conf)
    dialog.run()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()