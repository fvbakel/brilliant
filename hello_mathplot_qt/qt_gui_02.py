import PySimpleGUIQt as sg
import logging
import cv2

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import cv2

import timeit

class MyDialog:

    def __init__(self):

        self.show_img = None 
        self.show_max_width = 600
        self.show_img_dim = (self.show_max_width,400)
        self._cnt=0
        self._step=1

        pic_frame = [
            [sg.Image(filename='', key='_IMAGE_',size=self.show_img_dim)]
        ]

        ctrl_frame = [ 
            [   sg.Text('Control Frame')]
        ]

        layout = [  
            [sg.Frame("", ctrl_frame),sg.Frame("", pic_frame)]
        ]
        self._init_plot()
        self.window = sg.Window('Mathplot and QT test', layout=layout,return_keyboard_events=True)

    def update_data(self):

        self._t = np.arange(0.0 + self._cnt, 7.0 + self._cnt, self._step)
        #self._s = np.sin(np.pi * self._t)
        self._s = np.sin(self._t)
        self._cnt += self._step

    def _init_plot(self):
        # Data for plotting
        self.update_data()

        self._fig, self._ax = plt.subplots()
        self._canvas = FigureCanvasAgg(self._fig)
        self._line, = self._ax.plot(self._t, self._s)

        self._ax.set(xlabel='time (s)', ylabel='voltage (mV)',
            title='About as simple as it gets, folks')
        self._ax.grid()

        self._canvas.draw()
        buf = self._canvas.buffer_rgba()
        self._plt_img = np.asarray(buf)

    def update_plot(self):
        self._line.set_data(self._t, self._s)
        plt.xlim(self._t[0],self._t[-1])
        #self._line.figure.canvas.draw()
        self._canvas.draw()
        #self._fig.draw()

    def update_current_images(self):
        if not self._plt_img  is None:
            self.show_img=cv2.resize(self._plt_img, self.show_img_dim, interpolation = cv2.INTER_AREA)

    def update_dialog(self):
        self.update_data()
        self.update_plot()
        self.update_current_images()
        if not self.show_img is None:
            imgbytes=cv2.imencode('.png', self.show_img)[1].tobytes()
            self.window.FindElement('_IMAGE_').Update(data=imgbytes)
        

    def run(self):
        while True:
            event, values = self.window.Read(timeout=20, timeout_key='timeout')
            if event is None or event == '__QUIT__':
                break
            self.update_dialog()
        self.window.close()

def main():
    dialog = MyDialog()
    dialog.run()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()