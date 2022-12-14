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


class MotionDetectDialog:
    def __init__(self,motion_detector:MotionDetector):
        self.motion_detect = motion_detector
        self.right_width = 200
        self.video_max_width = 600
        self.video_max_height = 600
        left_frame = [
            [sg.Image(filename='', key='_IMAGE_')]
        ]
        right_frame = [ 
            [sg.Button('Quit',key='__QUIT__',size=(self.right_width + 5,sg.DEFAULT_ELEMENT_SIZE[1]))]
        ]
        layout = [  
            [sg.Frame("", left_frame),sg.Frame("", right_frame)]
        ]
        self.window = sg.Window('Motion detection', layout)

        self.cap = cv2.VideoCapture(self.motion_detect.configuration.data_dir + "/VID20221213155812.mp4")
        self.debug_fps()
        ret, self.frame = self.cap.read()
        #self.dump_frame()

        h, w = self.frame.shape[:2]
        rw = self.video_max_width / float(w)
        rh = self.video_max_height / float(h)
        
        h_for_w= int(h * rw)
        w_for_h= int(w * rh)
        
        if h_for_w > self.video_max_height:
            self.video_dim= (w_for_h, self.video_max_height)
        else:
            self.video_dim= (self.video_max_width, h_for_w)


        
        self.smaller = cv2.resize(self.frame, self.video_dim, interpolation = cv2.INTER_AREA)

    def dump_frame(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        cv2.imwrite(self.motion_detect.configuration.data_dir + "/frame_" +timestamp+ ".png", self.frame)

    def debug_fps(self):
        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    
        if int(major_ver)  < 3 :
            fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
            print ("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
        else :
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            print ("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
 

    def update_current_images(self):
        if  self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                self.smaller= cv2.resize(self.frame, self.video_dim, interpolation = cv2.INTER_AREA)

    def update_dialog(self):
        self.update_current_images()
        imgbytes=cv2.imencode('.png', self.smaller)[1].tobytes()
        self.window.FindElement('_IMAGE_').Update(data=imgbytes)
    
    def run(self):
        while True:
            event, values = self.window.Read(timeout=20, timeout_key='timeout')
            if event is None or event == '__QUIT__':
                break

            self.update_dialog()

        self.window.close()
        self.cap.release()

def main():
    config = Configuration()
    detector = MotionDetector(config)
    dialog = MotionDetectDialog(detector)
    dialog.run()
    cv2.destroyAllWindows()

main()
