import PySimpleGUIQt as sg
import numpy as np
import os
import cv2
from datetime import datetime
from PIL import Image
from pathlib import Path
import logging

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
        self.number_of_frames:int = 0
        self.current_frame_num:int = -1
        self.frames:list = None
        self.cached = False

    def open_file(self,filename:str):
        self.filename = filename
        self.cap = cv2.VideoCapture(filename)
        self.set_fps()
        self.set_props()
        #self.read_frame()
        self.current_frame_num = -1
        self.cache_frames()


    def cache_frames(self):
        self.frames = []
        while True:
            ret = self._read_frame_from_file()
            if not ret:
                break
            self.frames.append(self.frame)
        self.cached = True
        self.set_begin()


    def set_fps(self):
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    
        if int(major_ver)  < 3 :
            self.fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
        else :
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
    
    def set_props(self):
        if self.cap is not None:
            self.number_of_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def set_begin(self):
        self.set_frame(0)

    def set_frame(self,frame_number:int):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
        self.current_frame_num = -1
        self.read_frame()

    def read_frame(self):
        if self.cached:
            return self._read_from_cache()
        else:
            return self._read_frame_from_file()

    def _read_from_cache(self):
        if self.current_frame_num < (len(self.frames) -1):
            self.current_frame_num += 1
            self.frame = self.frames[self.current_frame_num]
            return True
        return False

    def _read_frame_from_file(self):
        ret = False
        if  self.cap is not None and self.cap.isOpened():
            ret, self.frame = self.cap.read()
            self.current_frame_num += 1
        return ret
    
    def dump_curent_frame(self):
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
        self.scale_org_to_result: tuple(float,float) = None
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
        self.scale_org_to_result = ( h_res/float(h), w_res/float(w))

    def org_to_res(self,location:tuple[int,int]):
        h, w = location
        h_scale, w_scale = self.scale_org_to_result
        h_res = int(h*h_scale)
        w_res = int(w*w_scale)
        return (h_res,w_res)
    
    def res_to_org(self,location:tuple[int,int]):
        h, w = location
        h_scale, w_scale = self.scale_org_to_result
        h_res = int(h/h_scale)
        w_res = int(w/w_scale)
        return (h_res,w_res)

class MotionController:

    def __init__(self, configuration:Configuration):
        self.configuration = configuration
        self.play =False
        self.detector = MotionDetector(self.configuration)
        self.timeout = 20
        self.out_resized = None
        self.dim_scale: DimensionScale = None
        self.img_updated = False

    @property
    def fps(self):
        if self.detector is None or self.detector.fps is None:
            return 0.0
        return self.detector.fps
    
    @property
    def current_frame(self):
        if self.detector is None:
            return None
        return  self.detector.frame

    @property
    def current_frame_num(self):
        if self.detector is None or self.detector.current_frame_num is None:
            return 0
        return  self.detector.current_frame_num

    @property
    def number_of_frames(self):
        if self.detector is None or self.detector.number_of_frames is None:
            return 0
        return self.detector.number_of_frames

    @property
    def duration(self):
        if self.detector is None or self.detector.fps is None:
            return 0.0
        return self.detector.number_of_frames / self.detector.fps
    
    @property
    def current_timestamp(self):
        if self.detector is None or self.detector.fps is None:
            return 0.0
        return (self.detector.current_frame_num +1) / self.detector.fps


    def open_file(self,filename:str):
        self.detector.open_file(filename)
        self.dim_scale = DimensionScale(self.detector.frame.shape[:2],self.configuration.max_dim)
        self.make_smaller()

    def set_begin(self):
        self.detector.set_begin()
        self.play = False
        self.make_smaller()

    def make_smaller(self):
        self.out_resized= cv2.resize(self.detector.frame, self.dim_scale.result_dim, interpolation = cv2.INTER_AREA)
        self.img_updated = True

    def update_current_images(self):
        if self.play:
            ret = self.detector.read_frame()
            if ret:
                self.make_smaller()
            else:
                self.play = False

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
            [
                sg.Text("Duration:",size=(self.right_width - 50,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__DURATION__',size=( 55,sg.DEFAULT_ELEMENT_SIZE[1]))
            ],
            [
                sg.Text("Number of frames:",size=(self.right_width - 50,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__NUM_FRAMES__',size=( 55,sg.DEFAULT_ELEMENT_SIZE[1]))
            ],
            [
                sg.Text("Current frame:",size=(self.right_width - 50,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__CURRENT_FRAME__',size=( 55,sg.DEFAULT_ELEMENT_SIZE[1]))
            ],
            [
                sg.Text("Time (sec):",size=(self.right_width - 50,sg.DEFAULT_ELEMENT_SIZE[1])),
                sg.Text(str(0),key='__TIME__',size=( 55,sg.DEFAULT_ELEMENT_SIZE[1]))
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

        
    def do_update_cycle(self):
        self.controller.update_current_images()
        self.update_dialog()
    
    def update_radio_buttons(self):
        self.window.FindElement('__PLAY_ON__').Update(self.controller.play)
        self.window.FindElement('__PLAY_OFF__').Update(not self.controller.play)

    def update_dialog(self):
       
        fps_str = "{:.2f}".format(self.controller.fps)
        self.window.FindElement('__FPS__').Update(fps_str)

        duration_str = "{:.2f}".format(self.controller.duration)
        self.window.FindElement('__DURATION__').Update(duration_str)

        nr_frames_str = "{}".format(self.controller.number_of_frames)
        self.window.FindElement('__NUM_FRAMES__').Update(nr_frames_str)

        cur_frame_num_str = "{}".format(self.controller.current_frame_num)
        self.window.FindElement('__CURRENT_FRAME__').Update(cur_frame_num_str)

        time_str = "{:.2f}".format(self.controller.current_timestamp)
        self.window.FindElement('__TIME__').Update(time_str)

        if self.controller.img_updated:
            logging.debug("Setting new image")
            imgbytes=cv2.imencode('.png', self.controller.out_resized)[1].tobytes()
            self.window.FindElement('_IMAGE_').Update(data=imgbytes)
            self.controller.img_updated = False

    def run(self):
        while True:
            event, values = self.window.Read(timeout=self.controller.timeout, timeout_key='timeout')
            if event is None or event == '__QUIT__':
                break
            if event == '__PLAY_ON__':
                self.controller.play = values['__PLAY_ON__']
            if event == '__BEGIN__':
                self.controller.set_begin()
                self.update_radio_buttons()

            self.do_update_cycle()

        self.window.close()
        self.controller.close()
        

def main():
    config = Configuration()
    dialog = MotionDetectDialog(config)
    dialog.run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    TEST_TMP_DIR = "./tmp"
    logging.basicConfig(level=logging.DEBUG,filename=f"{TEST_TMP_DIR}/debug.log",filemode='w')
    main()
