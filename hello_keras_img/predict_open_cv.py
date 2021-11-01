import cv2 as cv # OpenCV computer vision library
import numpy as np # Scientific computing library 
import os
import sys

net = cv.dnn.readNetFromTensorflow('./frozen_models/frozen_graph.pb')

def predict(filename):
    inWidth = 10
    inHeight = 20
    img_cv2 = cv.imread(filename,cv.IMREAD_GRAYSCALE)
    
    resize_img = cv.resize(img_cv2  , (inWidth , inHeight), interpolation = cv.INTER_NEAREST)

    #print("[INFO]Image shape: ", img_cv2.shape)
    print("Scale=", (1.0 / 255))
    blob = cv.dnn.blobFromImage(resize_img,
                                    scalefactor=1.0 / 255
                                #    ,
                                #    size=(inWidth, inHeight),
                                #    mean=(0, 0, 0),
                                #    swapRB=False,
                                #    crop=False
                                    
                                    )
                                    
    cv.imwrite('resize_img_debug.png',resize_img)
    # blob = np.transpose(blob, (0,2,3,1)) 
    # print("[INFO]img shape: ", blob.shape)

    # Run a model
    net.setInput(blob)
    out = net.forward()

    # Get a class with a highest score.
    out = out.flatten()
    classId = np.argmax(out)

    print("Predicted Class index:", classId)

predict_num = sys.argv[1]
print("Predicting for: " + predict_num)
directory='/data/digits-data/Validation/' + str(predict_num)
#directory='/data/tmp/train'
for filename in os.listdir(directory):
    if filename.endswith(".png"):
        predict(os.path.join(directory, filename))
