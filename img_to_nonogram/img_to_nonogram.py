import numpy as np
from PIL import Image, ImageDraw
import cv2
from math import sqrt
from math import floor
import os
   
class NonogramMaker:
    
    def __init__(self,data_dir,filename):
        self.data_dir = data_dir
        self.filename = filename
        self.basename = os.path.splitext(filename)[0]
        self.full_basename = self.data_dir + os.sep + self.basename
        self.org_img = cv2.imread(data_dir + os.sep + filename)
        self.org_y_size = self.org_img.shape[0]
        self.org_x_size = self.org_img.shape[1]
        self.mod_img = None
        self.out_x_size = 0
        self.out_y_size = 0
    
    def sharpen(self):
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        self.mod_img = cv2.filter2D(self.mod_img, -1, kernel)
        self.write_img("sharpen")

    def black_white(self):
        grayImage = cv2.cvtColor(self.mod_img, cv2.COLOR_BGR2GRAY)
        (thresh, self.mod_img) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
        self.write_img("b_w")

    def re_size(self):
        (h, w) = self.mod_img.shape[:2]
        r = self.out_x_size / float(w)
        self.out_y_size = int(h * r)

        dim = (self.out_x_size, self.out_y_size)
        self.mod_img = cv2.resize(self.mod_img, dim, interpolation = cv2.INTER_AREA)
        self.write_img("resized")

    def prepare_image(self):
        self.mod_img = self.org_img
        self.re_size()
        self.sharpen()
        self.black_white()

    def write_img(self,message):
        cv2.imwrite(self.full_basename + "_" + message +".jpg",self.mod_img)

    def test_pixel(self):
        self.mod_img[0,0] = 125
        self.mod_img[1,0] = 125
        self.write_img("pixel")

    def to_nonogram(self):

        output = open   (   self.full_basename +\
                            "_" + str(self.out_x_size) +\
                            "_" + str(self.out_y_size) +\
                            ".txt",\
                            "w"\
                        )
        
        output.write("# Clue: " + self.basename +"\n" )
        output.write("#\n" )

        for x in range(self.out_x_size):
            black_count = 0
            previous_value = -1
            line = []
            for y in range(self.out_y_size):
                value = self.mod_img[x,y]
                if (value != previous_value and black_count>0):
                    line.append(black_count)
                    black_count = 0
                
                if (value == 0):
                    black_count += 1
                previous_value = value
            if black_count > 0:
                line.append(black_count)
            
            output.write(" ".join(str(i) for i in line)+"\n")

        output.write("\n" )
        for y in range(self.out_y_size):
            black_count = 0
            previous_value = -1
            line = []
            for x in range(self.out_x_size):
                value = self.mod_img[x,y]
                if (value != previous_value and black_count>0):
                    line.append(black_count)
                    black_count = 0
                
                if (value == 0):
                    black_count += 1
                previous_value = value
            if black_count > 0:
                line.append(black_count)
            
            output.write(" ".join(str(i) for i in line)+"\n")

        output.close()

    def make(self,x_size):
        self.out_x_size = x_size
        self.prepare_image()
        #self.test_pixel()
        self.to_nonogram()
        

if __name__ == "__main__":
    data_dir = "/data"
    filename = "me.jpg"
    maker = NonogramMaker(data_dir,filename)
    maker.make(45)