from maze import *
import PySimpleGUIQt as sg
import logging

class MazeConfiguration:

    def __init__(self):
        self.default_game_size = Size(4,4)

class MazeController:

    def __init__(self):
        self.show_short_path = False
        self.show_trace = False
        
        self.square_width = 1
        self.wall_width = 1
        self.maze_img = None

        self.nr_of_cols:int = 10
        self.nr_of_rows:int = 10
        self.manual_move:ManualMove = None
        self.move_behavior:str = None
        self.nr_started:int = 0
        self.nr_of_cycles:int = 0
        self._init_move_behaviors()
        self.generate_new()

    def _init_move_behaviors(self):
        self.move_behaviors:dict[str,AutomaticMove] = dict()
        for cls in AutomaticMove.__subclasses__():
            self.move_behaviors[cls.__name__] = cls
    
    def reset_game(self):
        self.manual_move = None
        self.nr_started = 0
        self.nr_of_cycles = 0
        self.fastest:int = -1
        self.game = MazeGame(self.maze_gen.maze,square_width=self.square_width,wall_width=self.wall_width)
        blank_map:dict(str,tuple[int,int,int]) = dict()
        blank_map[Material.FLOOR_MARKED.value] = Color.WHITE.value
        blank_map[Material.FLOOR_HIGHLIGHTED.value] = Color.WHITE.value
        self.renderer= ImageGameGridRender(self.game.game_grid,material_map=blank_map)
        self._add_finish_behavior()
        self._update_material_map()
        self.render()

    def generate_new(self):
        self.maze_gen =  MazeGenerator(Size(self.nr_of_cols,self.nr_of_rows))
        self.reset_game()

    def _update_material_map(self):
        if self.show_short_path:
            self.renderer.material_map[Material.FLOOR_MARKED.value] = (255,0,0)
        else:
            self.renderer.material_map[Material.FLOOR_MARKED.value] = Color.WHITE.value
        
        if self.show_trace:
            self.renderer.material_map[Material.FLOOR_HIGHLIGHTED.value] = (0,0,126)
        else:
            self.renderer.material_map[Material.FLOOR_HIGHLIGHTED.value] = Color.WHITE.value
        

    def render(self):
        self.renderer.render()
        self.maze_img = self.renderer.output
    
    def render_changed(self):
        self.renderer.render_changed()
        self.maze_img = self.renderer.output

    def set_show_short_path(self,value:bool):
        if self.show_short_path != value:
            self.show_short_path = value
            self._update_material_map()
            self.render()
    
    def set_show_trace(self,value:bool):
        if self.show_trace != value:
            self.show_trace = value
            self._update_material_map()
            self.render()

    def get_move_behavior_cls(self):
        return self.move_behaviors.get(self.move_behavior,RandomMove)

    def add_particle(self):
            particle = Particle()
            particle.trace_material = Material.FLOOR_HIGHLIGHTED
            behavior = self.game.game_grid.add_manual_content(particle,self.get_move_behavior_cls())
            if not behavior is None:
                self.nr_started += 1
                self.render_changed()

    def add_manual_particle(self):
        if self.manual_move == None:
            particle = Particle()
            particle.material = Material.PLASTIC_HIGHLIGHTED
            self.manual_move = self.game.game_grid.add_manual_content(particle,ManualMove)
            if not self.manual_move is None:
                self.nr_started += 1
                self.render_changed()

    def _add_finish_behavior(self):
        self.finish_behavior:list[FinishDetector] = self.game.game_grid.set_behavior_last_spots(FinishDetector)

    def move_manual_particle(self,direction:Direction):
        if self.manual_move != None:
            self.manual_move.set_move(direction)

    def do_one_cycle(self):
        self.game.game_grid.do_one_cycle()
        if (self.nr_started -self.get_total_finished()) > 0:
            self.nr_of_cycles +=1
        self.render_changed()

    def get_total_finished(self):
        total = 0
        
        if self.finish_behavior is None:
            return total
        for behavior in self.finish_behavior:
            total += len(behavior.finished)
            # TODO move to finish behavior?
            if total > 0:
                min_steps = min(behavior.nr_of_steps)
                if self.fastest > min_steps or self.fastest == -1:
                    self.fastest = min_steps
        return total
    
    


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
                sg.Radio('On', 2,enable_events=True,key='__SHORT_ON__'),
                sg.Radio('Off', 2, default=True,key='__SHORT_OFF__')
            ],
            [   sg.Text('Show trace'),
                sg.Radio('On', 3,enable_events=True,key='__TRACE_ON__'),
                sg.Radio('Off', 3, default=True,key='__TRACE_OFF__')
            ],
            [sg.Text('Move behavior')],
            [sg.DropDown(list(self.controller.move_behaviors.keys()),default_value=self.controller.move_behavior ,key='__MOVE BEHAVIOR__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Manual particle',key='__MANUAL_PARTICLE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Add particle',key='__ADD_PARTICLE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],

            [sg.Text('Nr of columns',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Slider(range=(1,50),key='__NR_OF_COLS__',default_value=self.controller.nr_of_cols,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Text('Nr of rows')],
            [sg.Slider(range=(1,40),key='__NR_OF_ROWS__',default_value=self.controller.nr_of_rows,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],

            [sg.Text('Square width',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Slider(range=(1,20),key='__SQUARE_WIDTH__',default_value=self.controller.square_width,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Text('Wall width')],
            [sg.Slider(range=(1,20),key='__WALL_WIDTH__',default_value=self.controller.wall_width,orientation='h',size=(self.right_width,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Reset maze',key='__RESET_MAZE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Generate new',key='__GENERATE__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Quit',key='__QUIT__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))]
        ]

        stats_frame = [
            [   sg.Text("Total cycles:",size=(self.right_width - 25,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__NR_CYCLES__')
            ],
            [   sg.Text("Total started:",size=(self.right_width - 25,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__NR_STARTED__')
            ],
            [   sg.Text("Total finished:",size=(self.right_width - 25,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__NR_FINISHED__')
            ],
            [   sg.Text("Fastest:",size=(self.right_width - 25,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__FASTEST__')
            ]
        ]

        bottom_frame = [
            [sg.Text('',key='__STATUS__')]
        ]

        layout = [  
            [sg.Frame("", right_frame),sg.Frame("", left_frame)],
            [sg.Frame("",stats_frame)],
            [sg.Frame("",layout=bottom_frame)]
        ]
        self.window = sg.Window('Maze simulator', layout=layout,return_keyboard_events=True)

    def update_current_images(self):
        if not self.controller.maze_img is None:
            self.maze_display_img= cv2.resize(self.controller.maze_img, self.maze_img_dim, interpolation = cv2.INTER_AREA)

    def update_statistics(self):
        self.window.FindElement('__NR_CYCLES__').Update(str(self.controller.nr_of_cycles))
        self.window.FindElement('__NR_STARTED__').Update(str(self.controller.nr_started))
        self.window.FindElement('__NR_FINISHED__').Update(str(self.controller.get_total_finished()))
        self.window.FindElement('__FASTEST__').Update(str(self.controller.fastest))

    def update_dialog(self):
        self.controller.do_one_cycle()
        self.update_current_images()
        self.update_statistics()
        if not self.maze_display_img is None:
            imgbytes=cv2.imencode('.png', self.maze_display_img)[1].tobytes()
            self.window.FindElement('_IMAGE_').Update(data=imgbytes)

    def run(self):
        while True:
            event, values = self.window.Read(timeout=20, timeout_key='timeout')
            #logging.debug(f"event='{event}'")
            if event is None or event == '__QUIT__':
                break
            if event == 'a':
                self.controller.move_manual_particle(Direction.LEFT)
            if event == 'w':
                self.controller.move_manual_particle(Direction.UP)
            if event == 's':
                self.controller.move_manual_particle(Direction.DOWN)
            if event == 'd':
                self.controller.move_manual_particle(Direction.RIGHT)
            if event == '__MANUAL_PARTICLE__':
                logging.debug("Manual particle")
                self.controller.add_manual_particle()
            if event == '__ADD_PARTICLE__':
                logging.debug("Add particle")
                self.controller.add_particle()
            if event == '__RESET_MAZE__':
                logging.debug("Resetting maze")
                self.controller.reset_game()
                logging.debug("Reset maze ready")
            if event == '__GENERATE__':
                logging.debug("Generate button pressed")
                self.set_status_message('Generating new')
                self.controller.generate_new()
                self.set_status_message('')
            if event == '__SHORT_ON__':
                self.controller.set_show_short_path(values['__SHORT_ON__'])
            if event == '__TRACE_ON__':
                self.controller.set_show_trace(values['__TRACE_ON__'])
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
            self.update_move_behavior(values['__MOVE BEHAVIOR__'])
            

            self.update_dialog()
        self.window.close()

    # TODO: Move to contoller and add meaning full status updates to the controller
    def set_status_message(self,msg:str):
        self.window.FindElement('__STATUS__').Update(msg)

    def update_nr_of_cols(self,value:int):
        self.controller.nr_of_cols = value

    def update_nr_of_rows(self,value:int):
        self.controller.nr_of_rows = value

    def update_square_width(self,value:int):
        self.controller.square_width = value

    def update_wall_width(self,value:int):
        self.controller.wall_width = value

    def update_move_behavior(self,value:str):
        self.controller.move_behavior = value

def main():
    conf = MazeConfiguration()
    dialog = MazeDialog(conf)
    dialog.run()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    main()