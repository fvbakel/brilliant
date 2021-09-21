import numpy as np
from PIL import Image, ImageDraw
import cv2
from math import sqrt
from math import floor
import os
from argparse import ArgumentParser
   
class NonogramMaker:
    
    def __init__(self,filename):
        self.filename = filename
        self.basename = os.path.splitext(filename)[0]
        self.org_ext = os.path.splitext(filename)[1]
        self.org_img = cv2.imread(filename)
        if self.org_img is None:
            print("ERROR: Unable to read file: %s" %(filename))
            return
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
        global debug
        if debug:
            cv2.imwrite(self.basename + "_" + message + self.org_ext,self.mod_img)

    def test_pixel(self):
        self.mod_img[0,0] = 125
        self.mod_img[1,0] = 125
        self.mod_img[2,0] = 125
        self.write_img("pixel")

    def write_line(self,output, line):
        if len(line) > 0:
            output.write(" ".join(str(i) for i in line)+"\n")
        else:
            output.write("0\n")

    def to_nonogram(self):

        output = open   (   self.basename +\
                            "_" + str(self.out_x_size) +\
                            "_" + str(self.out_y_size) +\
                            ".txt",\
                            "w"\
                        )
        
        output.write("# Clue: " + self.basename +"\n" )
        output.write("#\n" )

        for x in range(self.mod_img.shape[0]):
            black_count = 0
            previous_value = -1
            line = []
            for y in range(self.mod_img.shape[1]):
                value = self.mod_img[x,y]
                if (value != previous_value and black_count>0):
                    line.append(black_count)
                    black_count = 0
                
                if (value == 0):
                    black_count += 1
                previous_value = value
            if black_count > 0:
                line.append(black_count)
            
            self.write_line(output, line)

        output.write("\n" )
        for y in range(self.mod_img.shape[1]):
            black_count = 0
            previous_value = -1
            line = []
            for x in range(self.mod_img.shape[0]):
                value = self.mod_img[x,y]
                if (value != previous_value and black_count>0):
                    line.append(black_count)
                    black_count = 0
                
                if (value == 0):
                    black_count += 1
                previous_value = value
            if black_count > 0:
                line.append(black_count)
            
            self.write_line(output, line)

        output.close()

    def make(self,x_size):
        if self.org_img is not None:
            self.out_x_size = x_size
            self.prepare_image()
            #self.test_pixel()
            self.to_nonogram()
        
debug =False
if __name__ == "__main__":
    parser = ArgumentParser(description="Convert image to nonogram puzzle\n")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("--file", "-f", help="Filename of the image", type=str, required=True)

    parser.add_argument("--nr_of_cols", "-x", help="Number of columns in the output", type=int, default=45, required=False)
    parser.add_argument("--debug", "-v", help="Output images of in between results", action="store_true")

    args = parser.parse_args()
    filename =args.file
    nr_of_cols = args.nr_of_cols
    debug = args.debug

    maker = NonogramMaker(filename)
    maker.make(nr_of_cols)
