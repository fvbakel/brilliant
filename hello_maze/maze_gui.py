from maze import MazeController,Direction
import PySimpleGUIQt as sg
import logging
import cv2

class MazeDialog:

    def __init__(self):
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
            [   sg.Text('Automatic add'),
                sg.Radio('On', 4,enable_events=True,key='__ADD_ON__'),
                sg.Radio('Off', 4, default=True,key='__ADD_OFF__')
            ],
            [   sg.Text('Run simulation'),
                sg.Radio('On', 5,enable_events=True,key='__SIM_ON__'),
                sg.Radio('Off', 5, default=True,key='__SIM_OFF__')
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
            if event == '__ADD_ON__':
                self.controller.set_auto_add(values['__ADD_ON__'])
            if event == '__SIM_ON__':
                self.controller.set_sim(values['__SIM_ON__'])
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
    dialog = MazeDialog()
    dialog.run()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    main()