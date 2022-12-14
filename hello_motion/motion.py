import PySimpleGUIQt as sg
import numpy as np
import os
import cv2
from datetime import datetime
from PIL import Image
from pathlib import Path

class Configuration:

    def __init__(self):
        self.data_dir = "/home/fvbakel/anna_data/falling_cone"
        
        self.max_width = 600
        self.max_height = 600
        self.max_dim = (self.max_height,self.max_width)

class MotionDetector:
    def __init__(self, configuration:Configuration):
        self.configuration = configuration
        self.filename:str = None
        self.frame = None
        self.fps:float = None
        self.cap = None
        self.amount_of_frames:int = None
        self.current_frame:int = None

    def open_file(self,filename:str):
        self.filename = filename
        self.cap = cv2.VideoCapture(filename)
        self.set_fps()
        self.read_frame()
        self.current_frame = 0

    def set_fps(self):
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    
        if int(major_ver)  < 3 :
            self.fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
        else :
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
    
    def set_props(self):
        if self.cap is not None:
            self.amount_of_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    def set_begin(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, -1)
        self.read_frame()
        self.current_frame = 0

    def set_frame(self,frame_number:int):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
        self.current_frame = frame_number
        self.read_frame()

    def read_frame(self):
        ret = False
        if  self.cap is not None and self.cap.isOpened():
            ret, self.frame = self.cap.read()
        return ret
    
    def dump_frame(self):
        if self.frame is not None:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            cv2.imwrite(self.configuration.data_dir + "/frame_" +timestamp+ ".png", self.frame)

    def close(self):
        if self.cap is not None:
            self.cap.release()

    def __del__(self):
        self.close()

class DimensionScale:

    def __init__(self,org_dim:tuple[int,int],max_dim:tuple[int,int]):
        self.org_dim = org_dim
        self.max_dim = max_dim
        self.result_dim: tuple(int,int) = None
        self.scale_org_to_result: tuple(int,int) = None
        self.scale_result_to_org: tuple(int,int) = None
        self.init_derived()

    def init_derived(self):
        h, w = self.org_dim
        h_max,w_max = self.max_dim
        rw = w_max / float(w)
        rh = h_max / float(h)
        
        h_for_w= int(h * rw)
        w_for_h= int(w * rh)
        
        if h_for_w > h_max:
            self.result_dim= (w_for_h, h_max)
        else:
            self.result_dim= (w_max, h_for_w)

        h_res, w_res = self.result_dim
        self.scale_org_to_result = (int(h_res/float(h)), int(w_res/float(w)))
        self.scale_result_to_org = (int(h/float(h_res)), int(w/float(w_res)))

class MotionController:

    def __init__(self, configuration:Configuration):
        self.configuration = configuration
        self.play =False
        self.detector = MotionDetector(self.configuration)
        self.full_update = False
        self.timeout = 20
        self.out_resized = None
        self.dim_scale: DimensionScale = None

    def open_file(self,filename:str):
        self.detector.open_file(filename)
        self.dim_scale = DimensionScale(self.detector.frame.shape[:2],self.configuration.max_dim)
        # todo, move resizing to separate class or function
        """   h, w = self.detector.frame.shape[:2]
        rw = self.configuration.video_max_width / float(w)
        rh = self.configuration.video_max_height / float(h)
        
        h_for_w= int(h * rw)
        w_for_h= int(w * rh)
        
        if h_for_w > self.configuration.video_max_height:
            self.video_dim= (w_for_h, self.configuration.video_max_height)
        else:
            self.video_dim= (self.configuration.video_max_width, h_for_w)
        """
        self.make_smaller()
        self.full_update = True

    def set_begin(self):
        self.detector.set_begin()
        self.play = False
        self.make_smaller()

    def make_smaller(self):
        self.out_resized= cv2.resize(self.detector.frame, self.dim_scale.result_dim, interpolation = cv2.INTER_AREA)

    def update_current_images(self):
        if self.play:
            ret = self.detector.read_frame()
            if ret:
                self.make_smaller()
            else:
                self.play = False
                self.full_update = True

    def close(self):
        if self.detector is not None:
            self.detector.close()


class MotionDetectDialog:
    def __init__(self, configuration:Configuration):
        self.configuration = configuration
        self.controller = MotionController(self.configuration) 
        self.right_width = 200
        left_frame = [
            [sg.Image(filename='', key='_IMAGE_')]
        ]
        right_frame = [        
            [
                sg.Text("FPS:",size=(self.right_width - 50,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__FPS__',size=( 55,sg.DEFAULT_ELEMENT_SIZE[1]))
            ],
            [   sg.Text('Play'),
                sg.Radio('On', 1,enable_events=True, default=self.controller.play,key='__PLAY_ON__'),
                sg.Radio('Off', 1, default=not self.controller.play,key='__PLAY_OFF__')
            ],
            [sg.Button('Begin',key='__BEGIN__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))],
            [sg.Button('Quit',key='__QUIT__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))]
        ]
        layout = [  
            [sg.Frame("", left_frame),sg.Frame("", right_frame)]
        ]
        self.window = sg.Window('Motion detection', layout)

        self.controller.open_file(self.configuration.data_dir + "/VID20221213155812.mp4")

        
    def update_dialog(self):
        self.controller.update_current_images()
        self.update_image()
        if self.controller.full_update:
            self.full_update_dialog()

    def update_image(self):
        imgbytes=cv2.imencode('.png', self.controller.out_resized)[1].tobytes()
        self.window.FindElement('_IMAGE_').Update(data=imgbytes)
    
    def full_update_dialog(self):
        self.controller.full_update = False
        self.window.FindElement('__PLAY_ON__').Update(self.controller.play)
        self.window.FindElement('__PLAY_OFF__').Update(not self.controller.play)

        if self.controller.detector is not None and self.controller.detector.fps is not None:
            fps_str = "{:.2f}".format(self.controller.detector.fps)
        self.window.FindElement('__FPS__').Update(fps_str)

        self.update_image()

    def run(self):
        while True:
            event, values = self.window.Read(timeout=self.controller.timeout, timeout_key='timeout')
            if event is None or event == '__QUIT__':
                break
            if event == '__PLAY_ON__':
                self.controller.play = values['__PLAY_ON__']
            if event == '__BEGIN__':
                self.controller.set_begin()
                self.full_update_dialog()

            self.update_dialog()

        self.window.close()
        self.controller.close()
        

def main():
    config = Configuration()
    dialog = MotionDetectDialog(config)
    dialog.run()
    cv2.destroyAllWindows()

main()
