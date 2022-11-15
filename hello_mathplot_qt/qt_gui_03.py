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
        self._step=0.1

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

        self._t = ['Dummy','Other']
        self._s = [10,self._cnt]
        self._cnt += self._step

    def _init_plot(self):
        # Data for plotting
        self.update_data()

        self._fig, self._ax = plt.subplots(2,2)
        self._canvas = FigureCanvasAgg(self._fig)
        #self._line, = self._ax.plot(self._t, self._s)
        self._bar = self._ax[0][0].bar(['Dummy'],[10])

        self._ax[0][0].set(xlabel='What?', ylabel='Percentage',
            title='Bar example')
        self._ax[0][1].set(xlabel='What 2?', ylabel='Percentage',
            title='Bar example 2')
        self._ax[1][0].set(xlabel='What 3?', ylabel='Percentage',
            title='Bar example 3')
        self._ax[1][1].set(xlabel='What 4?', ylabel='Percentage',
            title='Bar example 4')

        self._fig.suptitle('Some different bar charts')
        self._fig.tight_layout(h_pad=2)

        self._canvas.draw()
        buf = self._canvas.buffer_rgba()
        self._plt_img = np.asarray(buf)
        plt.show()

    def update_plot(self):       
        self._bar.remove()
        self._bar = self._ax[0][0].bar(self._t,self._s)
        self._bar[0].set_color('green')
        self._bar[1].set_color('red')

        self._canvas.draw()


    def update_current_images(self):
        if not self._plt_img  is None:
            self.show_img=cv2.resize(self._plt_img, self.show_img_dim, interpolation = cv2.INTER_AREA)
            self.show_img = cv2.cvtColor(self.show_img, cv2.COLOR_BGR2RGB)

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